from random import random
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from VKServer.processing import *


def write_msg(user_id, message=None, keyboard=None):
    vk.method('messages.send', {'user_id': user_id,
                                'random_id': random(),
                                'message': message,
                                'keyboard': keyboard})


def create_keybard(labels):
    keyboard = VkKeyboard(one_time=True)

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
        print(event.text)
        user_id = event.user_id
        first_name = user(event.user_id)[0]["first_name"]
        last_name = user(event.user_id)[0]["last_name"]
        if event.text == 'Начать':
            print(get_status(user_id))
            authorization = register_the_server(user_id, first_name, last_name)
            write_msg(user_id, message=str(authorization), keyboard=create_keybard(
                ['Категории',
                 'Ключевые слова']))
        elif event.text == 'Категории':
            print(get_status(user_id))
            category = subscribe_category_get(user_id)
            write_msg(user_id, message=category['message'], keyboard=create_keybard(category['button']))
        elif event.text == 'Ключевые слова':
            print(get_status(user_id))
            keyword = subscribe_keywords_get(user_id)
            if keyword['button']:
                write_msg(user_id, message=keyword['message'], keyboard=create_keybard(keyword['button']))
            else:
                write_msg(user_id, message=keyword['message'])
        elif get_status(user_id) == 3:
            add_cat = subscribe_category_add(user_id, event.text)
            write_msg(user_id, message=add_cat['message'])
        elif get_status(user_id) == 4:
            add_key = subscribe_keywords_add(user_id, event.text)
            write_msg(user_id, message=add_key['message'])
        elif get_status(user_id) == 5:
            pass
        elif get_status(user_id) == 6:
            pass









