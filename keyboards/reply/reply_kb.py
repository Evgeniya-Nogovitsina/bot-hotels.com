from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def choise_amount() -> ReplyKeyboardMarkup:
    """
    Кнопки выбора количества(отелей в результате, фото)
    """
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_one = KeyboardButton(text='3')
    btn_two = KeyboardButton(text='5')
    btn_three = KeyboardButton(text='7')
    btn_four = KeyboardButton(text='10')
    kb.add(btn_one, btn_two, btn_three, btn_four)
    return kb


def answer() -> ReplyKeyboardMarkup:
    """
    Подтверждение(нужно ли фото, правильно ли введены данные для поиска)
    """
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_one = KeyboardButton(text='Да')
    btn_two = KeyboardButton(text='Нет')
    kb.add(btn_one, btn_two)
    return kb
