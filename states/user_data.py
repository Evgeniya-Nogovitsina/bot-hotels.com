from telebot.handler_backends import State, StatesGroup


class UserData(StatesGroup):
    """
    Класс состояний пользователя.
    """
    command = State()
    sorting = State()
    city_id = State()
    city = State()
    check_in = State()
    check_out = State()
    period = State()
    hotel_amount = State()
    photo_amount = State()
    distance = State()
    price_range = State()
