import json

from FlaskServer.database_working import request_db
from FlaskServer.NewsAPI import pool_news


NewsApiKey = 'c6708f79471a46dc8f6b3b783b1aa4bc'
db = request_db('tesst')
print(db)


def db_toList(response_db):
    """
    Преобразует ответ БД в тип list, исключая кортежи и запятые, для удобства итерации/
    Работает, если ответ от БД имеет только одну колоку
    :param response_db: Ответ от Базы данных
    :return: list
    """
    values_list = []
    for name in response_db:
        values_list.append(name[0])
    return values_list


def get_users(data):
    """
    Возвращает пользователя по любому из параметров:
    :param data: requests.args
    :return: type: json, response: {result, code}
    :parameter UserId: vkUserId, FirstName, LastName
    OR
    :parameter VKid: id, FirstName, LastName
    """
    if 'UserId' not in data and 'VKid' not in data:
        return {
            "result": json.dumps({"status": "ERROR", "message": "Bad request"}),
            "code": 400
        }

    try:
        if 'UserId' in data:
            data_table = db.request_select('vkUserId, FirstName, LastName', 'users', 'id', int(data['UserId']))
            return {
                "result": json.dumps({
                    "vkUserId": data_table[0][0],
                    "FirstName": data_table[0][1],
                    "LastName": data_table[0][2]
                }),
                "code": 200
            }

        elif 'VKid' in data:
            data_table = db.request_select('id, FirstName, LastName', 'users', 'vkUserId', data['VKid'])
            return {
                "result": json.dumps({
                    "id": data_table[0][0],
                    "FirstName": data_table[0][1],
                    "LastName": data_table[0][2]
                }),
                "code": 200
            }
    except IndexError:
        return {
            "result": json.dumps({"status": "ERROR", "message": "no value specified"}),
            "code": 400
        }


def create_user(data):
    """
    Регистрация пользователя
    :parameter required: FirstName; LastName
    :param data: requests.args
    :return: type(json)
    """
    if 'FirstName' not in data or 'LastName' not in data:
        return {
            "result": json.dumps({"status": "ERROR", "message": "Bad request"}),
            "code": 400
        }

    value_id = db.request_insert('users', 'vkUserId, FirstName, LastName',
                                 data['vkUserId'] if data['vkUserId'] else 0, data['FirstName'], data['LastName'])
    return {
        "result": json.dumps({"status": "OK", 'UserId': value_id[0][0]}),
        "code": 200
    }


def get_categories(data):
    """
    Показать активные подписки на категории по выбраному пользователю
    :parameter required: UserId
    :param data: requests.args
    :return: type(json)
    """
    if 'UserId' not in data:
        return {
            "result": json.dumps({"status": "ERROR", "message": "Bad request"}),
            "code": 400
        }
    data_table = db.request_select_join(
        'categories.name',
        'categories',
        'relationCategory',
        'UserId',
        data['UserId']
    )
    return {
        "result": json.dumps({"categories": db_toList(data_table)}),
        "code": 200
    }


def create_categories(data):
    """
    Добавить подписку на определенную категорию
    :parameter required: UserId: value, category: value
    :param data: requests.args
    :return: json: status: OK
    OR
    :return: json: status: ERROR
    """
    if 'UserId' not in data or 'category' not in data:
        return {
            "result": json.dumps({"status": "ERROR", "message": "Bad request"}),
            "code": 400
        }
    # Валидность категории
    if data['category'] in db_toList(db.request_select('name', 'categories')):
        # Уникальность категории
        if data['category'] in db_toList(
                db.request_select_join('categories.name', 'categories', 'relationCategory', 'UserId', data['UserId'])
        ):
            return {
                "result": json.dumps({"status": "ERROR", "massage": "the selected category is added earlier"}),
                "code": 400
            }
        db.request_insert('relationCategory', 'UserId, CategoryId', data['UserId'],
                          db.request_select('id', 'categories', 'name', data['category'])[0][0])

        return {
            "result": json.dumps({"status": "OK"}),
            "code": 200
        }

    return {
        "result": json.dumps({"status": "ERROR", "massage": "Category does not exist"}),
        "code": 400
    }


def get_keywords(data):
    """
    Активные подписки по указанному пользователю
    :parameter required: UserId: value
    :param data:
    :return: json: keywords=list: [value1, value2, ... valueN]
    """
    if 'UserId' not in data:
        return {
            "result": json.dumps({"status": "ERROR", "message": "Bad request"}),
            "code": 400
        }
    data_table = db.request_select_join(
        'keywords.name',
        'keywords',
        'relationKeywords',
        'UserId',
        data['UserId'],
    )
    return {
        "result": json.dumps({"keywords": db_toList(data_table)}),
        "code": 200
    }


def create_keywords(data):
    """
    Добавление ключевого слова
    :parameter required: UserId: value; keyword: value
    :param data:
    :return:
    """
    if 'UserId' not in data or 'keyword' not in data:
        return {
            "result": json.dumps({"status": "ERROR", "message": "Bad request"}),
            "code": 400
        }
    # Наличие ключевого слова в БД
    if data['keyword'] is not db_toList(
            db.request_select('name', 'keywords')):
        db.request_insert_one('keywords', 'name', data['keyword'])
    # Проверка на унакальность
    if data['keyword'] is not db_toList(
            db.request_select_join(
                'keywords.name',
                'keywords',
                'relationKeywords',
                'UserId',
                data['UserId']
            )
    ):
        # Привязка ключевого слова к пользователю
        db.request_insert('relationKeywords', 'UserId, KeywordsId', data['UserId'],
                          db.request_select('id', 'keywords', 'name', data['keyword'])[0][0])
        return {
            "result": json.dumps({"status": "OK"}),
            "code": 200
        }
    return {
        "result": json.dumps({"status": "ERROR", "massage": "the selected keywords is added earlier"}),
        "code": 400
    }


def get_news(data):
    """
    Получение 10 новостей по категориям или ключевым словам
    :parameter required: UserId: value; mode: keywords OR categories
    :param data:
    :return:
    """
    if 'UserId' not in data or 'mode' not in data:
        return {
            "result": json.dumps({"status": "ERROR", "message": "Bad request"}),
            "code": 400
        }
    if data['mode'] == 'keywords':
        data_table = db.request_select_join(
            'keywords.name',
            'keywords',
            'relationKeywords',
            'UserId',
            data['UserId']
        )
    else:
        data_table = db.request_select_join(
            'categories.name',
            'categories',
            'relationCategory',
            'UserId',
            data['UserId']
        )
    actions = db_toList(data_table)
    if not actions:
        return {
            "result": json.dumps({"status": "ERROR", "message": "There are no active subscriptions"}),
            "code": 400
        }
    return {
        "result": json.dumps(pool_news(NewsApiKey, actions, funk=data['mode'])),
        "code": 200
    }
