import requests
from VKServer.status_users import *
URL = 'http://0.0.0.0:8080'


def request_data(url_cat, params, response, method="GET"):
    """
    Запрос на REST API сервер
    :param url_cat: url запроса
    :param params: Параметры запроса
    :param response: Ключ json ответа от сервера, который ожидаем
    :param method: methods GET, POST, DELETE (default = GET)
    :return: {status: статус ответа OK if status_code == 200 or status_code,
              message: response message text}
    """
    r = None
    if method == "GET":
        r = requests.get(f'{URL}/{url_cat}', params=params)
    elif method == "POST":
        r = requests.post(f'{URL}/{url_cat}', json=params)

    if r.status_code == 200:
        return {"status": "OK", "message": r.json()[response]}
    elif r.status_code != 500:
        return {"status": r.status_code, "message": r.json()['message']}
    else:
        return {"status": r.status_code, "message": "Крах Сервера"}


def register_the_server(VKUserId, first_name, last_name):
    """
    Авторизация пользователя
    :return: welcome message, type: text
    """
    result = request_data(url_cat='users',
                          response='id',
                          params={"VKid": VKUserId})
    if result['status'] == 400:
        params = {
            "vkUserId": VKUserId,
            "FirstName": first_name,
            "LastName": last_name
        }
        add = request_data(url_cat='users',
                           params=params,
                           response='UserId',
                           method='POST')
        if add['status'] == 400:
            return f'''
            Прошу прощения, возникла ошибка при регистрации пользователя на сервере:
            {add['message']}
            '''
    update_id(VKUserId, result['message'])
    update_status(VKUserId, MENU)
    return f'Рад видеть Вас, {first_name} {last_name}!'


def subscribe_category_all():
    return request_data('subscriptions/categories_all',
                        {'RUS': 'yes'},
                        'categories')


def subscribe_category_get(VKUserId):
    """
    Получение подписок на категории
    :param VKUserId: VK User Id
    :return: {message = message text, button: type button}
    """
    data_cat = request_data(url_cat='subscriptions/categories',
                            params={'UserId': get_id(VKUserId),
                                    'RUS': 'yes'},
                            response='categories')
    if data_cat['message']:
        return {
            "message": f'''
                       Вы подписаны на следующие категории:
                       {','.join([n for n in data_cat['message']])}
                       ''',
            "button": None}
    update_status(VKUserId, ADD_CATEGORY)
    return {"message": "У Вас нет активных подписок. Выберите категорию для добавления",
            "button": subscribe_category_all()['message']}


def subscribe_keywords_get(VKUserId):
    data_key = request_data('subscriptions/keywords', {'UserId': get_id(VKUserId)}, 'keywords')
    if data_key['message']:
        return {"message": f"Вы подписаны на следующие ключевые слова: {','.join([n for n in data_key['message']])}",
                "button": None}
    update_status(VKUserId, ADD_KEYWORD)
    return {"message": "У Вас нет активных подписок в данной категории. Введите ключевое слово для добавления",
            "button": None}


def subscribe_category_add(VKUserId, value):
    data_cat = request_data('subscriptions/categories',
                            {'UserId': get_id(VKUserId),
                             'category': value,
                             'RUS': 'yes'},
                            'status',
                            method='POST')
    if data_cat['status'].isdigit():
        return {'message': "Ошибка при добавлении категории"}
    return {'message': f"Категория {value} добавлена!"}


def subscribe_keywords_add(VKUserId, value):
    data_key = request_data('subscriptions/keywords',
                            {'UserId': get_id(VKUserId),
                             'keyword': value},
                            'status',
                            method='POST'
                            )
    if data_key['status'].isdigit():
        return {'message': "Ошибка при добавлении ключевого слова"}
    return {'message': f"Ключевое слово {value} добавлено!"}


def news_by_category(VKUserId):
    data_cat = request_data(url_cat='subscriptions/categories',
                            params={'UserId': get_id(VKUserId)},
                            response='categories')
    result = []
    for category in data_cat["message"]:
        news = request_data('news',
                            {'UserId': get_id(VKUserId),
                             'mode': 'categories'},
                            f'{category}')['message'][:10]
        result.extend(news)
    return result


def news_by_keyword(VKUserId):
    data_key = request_data('subscriptions/keywords', {'UserId': get_id(VKUserId)}, 'keywords')
    result = []
    for keyword in data_key["message"]:
        news = request_data('news',
                            {'UserId': get_id(VKUserId),
                             'mode': 'keywords'},
                            f'{keyword}')['message'][:10]
        result.extend(news)
    return result