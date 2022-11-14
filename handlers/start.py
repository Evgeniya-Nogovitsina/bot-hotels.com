from loguru import logger
from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message) -> None:
    """
    Стартовая команда бота. Выдает приветствие и список команд
    """
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | команда {message.text}')
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.send_message(
        message.from_user.id,
        f'Привет, {message.from_user.full_name}!\nВыбери нужную команду из списка:\n' + '\n'.join(text)
    )
