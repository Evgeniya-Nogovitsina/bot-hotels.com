from loguru import logger
from telebot.custom_filters import StateFilter

import handlers
from database.data_interaction import create_db
from loader import bot
from utils.set_bot_commands import set_default_commands

if __name__ == '__main__':
    create_db()
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    try:
        bot.infinity_polling()
    except Exception as ex:
        logger.error(f'Ошибка: {ex}')
