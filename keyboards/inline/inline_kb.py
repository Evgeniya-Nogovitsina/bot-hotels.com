from typing import Optional

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from hotel_requests.hot_req import city_search


def button_city(user_city: str) -> Optional[InlineKeyboardMarkup]:
    """
    Функция выводит клавиатуру с вариантами городов/районов.

    :param user_city: город, который ввел пользователь после выбора одной из команд
    :return: id выбранного места и его название
    """
    kb = InlineKeyboardMarkup(row_width=1)
    cities_dict = city_search(user_city=user_city)
    if cities_dict is not None:
        for name, city_id in cities_dict.items():
            btn = InlineKeyboardButton(text=name, callback_data=city_id + ':' + name)
            kb.add(btn)
        return kb
    else:
        return None

