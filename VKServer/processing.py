import requests
import json
from collections import defaultdict


START, MENU, ADD_CATEGORY, ADD_KEYWORD, NEWS_CATEGORY, NEWS_KEYWORD = range(6)
USER_ID = defaultdict(lambda: START)
MENU_STATUS = defaultdict(lambda: {})
Categories = {"entertainment": "Развлечения",
              "business": "Бизнес",
              "general": "Общее",
              "health": "Здоровье",
              "science": "Наука",
              "sports": "Спорт",
              "technology": "Технологии"}

URL = 'http://0.0.0.0:8080'


def get_id(VK_ID):
    return USER_ID[VK_ID]


def update_id(VK_ID, User_ID):
    USER_ID[VK_ID] = User_ID


def get_status(VK_ID):
    return MENU_STATUS[VK_ID]


def update_status(VK_ID, value):
    MENU_STATUS[VK_ID] = value


def request_data(url_cat, response, params, method="GET"):
    r = None
    if method == "GET":
        r = requests.get(f'{URL}/{url_cat}', params=params)
    elif method == "POST":
        r = requests.post(f'{URL}/{url_cat}', json=params)

    if r.status_code == 200:
        return {"status": "OK", "message": r.json()[response]}
    elif r.status_code == 400:
        return {"status": r.status_code, "message": r.json()['message']}


def register_the_server(VKUserId, first_name, last_name):
    result = request_data('users', 'id', {"VKid": VKUserId})
    print(result, result['status'])
    if result['status'] == 'OK':
        update_id(VKUserId, result['message'])
        update_status(VKUserId, MENU)
        return f'Рад видеть Вас, {first_name} {last_name}!'
    elif result['status'] == 400:
        params = {
            "vkUserId": VKUserId,
            "FirstName": first_name,
            "LastName": last_name
        }
        add = request_data('users', 'UserId', params, method='POST')
        if add['status'] == 'OK':
            update_id(VKUserId, add['message'])
            update_status(VKUserId, MENU)
            return f'Рад видеть Вас, {first_name} {last_name}!'

        elif add['status'] == 400:
            return f'''
            Прошу прощения, возникла ошибка при регистрации пользователя на сервере:
            {add['message']}
            '''


def subscribe_category_get(VKUserId):
    data_cat = request_data('subscriptions/categories', 'categories', {'UserId': get_id(VKUserId)})
    print(data_cat['message'])
    if data_cat['message']:
        update_status(VKUserId, NEWS_CATEGORY)
        return {"message": "Выберите категорию для получения новостей",
                "button": data_cat['message']}
    update_status(VKUserId, ADD_CATEGORY)
    return {"message": "У Вас нет активных подписок. Выберите категорию для добавления",
            "button": [Categories[key] for key in sorted(Categories)]}


def subscribe_keywords_get(VKUserId):
    data_key = request_data('subscriptions/keywords', 'keywords', {'UserId': get_id(VKUserId)})
    if data_key['message']:
        update_status(VKUserId, NEWS_KEYWORD)
        return {"message": "Выберите ключевые слова, для получения новостей",
                "button": data_key['message']}
    update_status(VKUserId, ADD_KEYWORD)
    return {"message": "У Вас нет активных подписок в данной категории. Введите ключевое слово для добавления",
            "button": None}


def subscribe_category_add(VKUserId, value):
    data_cat = request_data('subscriptions/categories', 'status',
                            {'UserId': get_id(VKUserId),
                             'category': value}, method='POST')
    if data_cat['status'].isdigit():
        return {'message': "Ошибка при добавлении категории"}
    return {'message': f"Категория {value} добавлена!"}


def subscribe_keywords_add(VKUserId, value):
    data_key = request_data('subscriptions/keywords', 'status',
                            {'UserId': get_id(VKUserId),
                             'keyword': value}, method='POST'
                            )
    if data_key['status'].isdigit():
        return {'message': "Ошибка при добавлении ключевого слова"}
    return {'message': f"Ключевое слово {value} добавлено!"}








