from loguru import logger
from telebot.types import Message

from database.data_interaction import data_request
from loader import bot


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """
    Команда запроса истории поиска гостиниц. Вызов функции data_request,
    которая после SQL-запроса возвращает словарь, содержащий в ключе
    команду, время, локацию. В значении: список гостиниц.
    """
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | команда {message.text}')
    bot.send_message(message.chat.id, 'История поиска (последние 5 запросов).')
    history_request = data_request(message.chat.id)
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | '
                f'функция {data_request.__name__} возвращает словарь с командами и списками отелей')
    for command, hotels_list in history_request.items():
        text = f"Время: {command[0]}\n" \
               f"Команда: {command[1]}\n" \
               f"Место поиска: {command[2]}\n"
        bot.send_message(message.from_user.id, text)
        hotel_info = 'Список гостиниц:\n' \
                     '====================\n'
        for hotel in hotels_list:
            hotel_info += f"Название: {hotel[0]}\n" \
                          f"Адрес: {hotel[1]}\n" \
                          f"Цена за сутки: {hotel[2]}\n" \
                          f"Ссылка: {hotel[3]}\n" \
                          f"====================\n"
        bot.send_message(message.from_user.id, hotel_info, disable_web_page_preview=True)
    bot.send_message(message.from_user.id, 'Выберите нужную команду или нажмите /help.')
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | вывод истории завершен')
