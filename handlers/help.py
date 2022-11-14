from loguru import logger
from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    """
    Команда-помощник. Выдает список доступных команд.
    """
    logger.info(f'Пользователь {message.from_user.full_name} | {message.chat.id} | команда {message.text}')
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.send_message(message.from_user.id, '\n'.join(text))
