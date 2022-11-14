from loguru import logger
from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_data import config

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

logger.add('info.log',
           format='{time} {level} {message}',
           level='INFO',
           rotation='5 MB',
           compression='zip')
