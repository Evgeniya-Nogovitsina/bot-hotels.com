from loguru import logger
from telebot.types import Message

from loader import bot


@bot.message_handler(content_types=['text'], func=lambda message: True)
def bot_echo(message: Message) -> None:
    logger.warning(f'Пользователь {message.from_user.full_name} | {message.chat.id} | ошибка ввода')
    bot.send_message(message.from_user.id, 'Я тебя не понимаю. Напиши /help')
