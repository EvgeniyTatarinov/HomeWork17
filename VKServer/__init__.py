from random import random
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from VKServer.processing import *
from VKServer.status_users import *


def write_msg(user_id, message=None, keyboard=None):
    vk.method('messages.send', {'user_id': user_id,
                                'random_id': random(),
                                'message': message,
                                'keyboard': keyboard})


def create_keybard(button_type='main_menu', labels=None):
    keyboard = VkKeyboard(one_time=True)
    if button_type == 'main_menu':
        keyboard.add_button(label='Новости', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(label='Управление подписками', color=VkKeyboardColor.PRIMARY)

    elif button_type == 'menu_subscriptions':
        keyboard.add_button(label='Категории', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button(label='Ключевые слова', color=VkKeyboardColor.DEFAULT)

    elif button_type == 'menu_category':
        keyboard.add_button(label='Добавить категорию', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label='Удалить категорию', color=VkKeyboardColor.NEGATIVE)

    elif button_type == 'menu_keyword':
        keyboard.add_button(label='Добавить ключевое слово', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label='Удалить', color=VkKeyboardColor.NEGATIVE)

    elif button_type == 'send_news':
        keyboard.add_button(label='Получить новости', color=VkKeyboardColor.POSITIVE)

    elif button_type == 'menu_back':
        keyboard.add_button(label='Назад', color=VkKeyboardColor.DEFAULT)

    elif button_type == 'mode':
        for label in range(len(labels)):
            if label <= 2:
                keyboard.add_button(label=labels[label], color=VkKeyboardColor.DEFAULT)
            elif label % 3 == 0:
                keyboard.add_line()
                keyboard.add_button(label=labels[label], color=VkKeyboardColor.DEFAULT)
            else:
                keyboard.add_button(label=labels[label], color=VkKeyboardColor.DEFAULT)

    return keyboard.get_keyboard()


def user(user_id):
    return vk.method('users.get', {'user_ids': user_id, 'fields': 'city'})


KEY = '803fb5f85822a79bc3721955f73fbd5de9830c9490b34b9900ba859499baddc1ecab5012e978f75ad11bf'
vk = VkApi(token=KEY)
longpoll = VkLongPoll(vk)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        user_id = event.user_id
        first_name = user(event.user_id)[0]["first_name"]
        last_name = user(event.user_id)[0]["last_name"]

        if event.text == 'Начать':
            # Авторизация пользователя
            authorization = register_the_server(user_id, first_name, last_name)
            write_msg(user_id, message=str(authorization), keyboard=create_keybard())

        elif event.text == 'Новости' and get_status(user_id) == MENU:
            update_status(user_id, NEWS)
            write_msg(user_id, 'Выберите раздел', create_keybard('menu_subscriptions'))

        elif event.text == 'Управление подписками':
            update_status(user_id, SET)
            write_msg(user_id, 'Выберите раздел', create_keybard('menu_subscriptions'))

        elif event.text == 'Категории':
            category = subscribe_category_get(user_id)
            # У пользоателя нет активных подписок на категории
            if get_status(user_id) == ADD_CATEGORY:
                write_msg(user_id, message=category['message'],
                          keyboard=create_keybard(labels=category['button'], button_type='mode'))
            # Запрашиваем новости по подпискам на категории
            elif get_status(user_id) == NEWS:
                update_status(user_id, NEWS_CATEGORY)
                write_msg(user_id, message=category['message'], keyboard=create_keybard('send_news'))
            # Изменение категорий
            elif get_status(user_id) == SET:
                write_msg(user_id, category['message'], create_keybard('menu_category'))

        elif event.text == 'Добавить категорию' and get_status(user_id) == SET:
            update_status(user_id, ADD_CATEGORY)
            all_cat = subscribe_category_all()
            write_msg(user_id, 'Выберите категорию', create_keybard('mode', all_cat['message']))

        elif event.text == 'Ключевые слова':
            keyword = subscribe_keywords_get(user_id)
            if get_status(user_id) == ADD_KEYWORD:
                write_msg(user_id, message=keyword['message'], keyboard=create_keybard('menu_back'))
            elif get_status(user_id) == NEWS:
                update_status(user_id, NEWS_KEYWORD)
                write_msg(user_id, message=keyword['message'], keyboard=create_keybard('send_news'))
            elif get_status(user_id) == SET:
                write_msg(user_id, message=keyword['message'], keyboard=create_keybard('menu_keyword'))

        elif event.text == 'Добавить ключевое слово' and get_status(user_id) == SET:
            update_status(user_id, ADD_KEYWORD)
            write_msg(user_id, 'Введите ключевое слово для добавления', create_keybard('menu_back'))

        elif event.text == 'Получить новости':
            if get_status(user_id) == NEWS_CATEGORY:
                news = news_by_category(user_id)
                for n in news:
                    write_msg(user_id, f"{n[0]} {n[1]} {n[2]}")
            elif get_status(user_id) == NEWS_KEYWORD:
                news = news_by_keyword(user_id)
                for n in news:
                    write_msg(user_id, f"{n[0]} {n[1]} {n[2]}")

        elif event.text == 'Назад':
            update_status(user_id, MENU)
            write_msg(user_id, message='Вы вернулись в Главное меню', keyboard=create_keybard())

        elif get_status(user_id) == ADD_CATEGORY:
            add_cat = subscribe_category_add(user_id, event.text)
            write_msg(user_id, message=add_cat['message'], keyboard=create_keybard('menu_back'))

        elif get_status(user_id) == ADD_KEYWORD:
            add_key = subscribe_keywords_add(user_id, event.text)
            write_msg(user_id, message=add_key['message'], keyboard=create_keybard('menu_back'))












