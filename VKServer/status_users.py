from collections import defaultdict


"""
function get_id: храним UserId сервера. 
function update_id: Обновляем UserId сервера
function get_status / update_status: Получение / изменение сстатуса пользователя 
"""

START, MENU, ADD_CATEGORY, ADD_KEYWORD, SET, DEL_CATEGORY, DEL_KEYWORD, NEWS, NEWS_CATEGORY, NEWS_KEYWORD = range(10)

USER = defaultdict(lambda: {})
MENU_STATUS = defaultdict(lambda: START)


def get_id(VKID):
    return USER[VKID]


def update_id(VKID, UserId):
    USER[VKID] = UserId


def get_status(VKID):
    return MENU_STATUS[VKID]


def update_status(VKID, user_status):
    MENU_STATUS[VKID] = user_status
