import os

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from utils.tgbot.tg_commands import id_command, moyai_command, message_processing, set_commands


def run():
    application = (Application.builder()
                   .token(os.getenv('TG_TOKEN'))
                   .post_init(set_commands)
                   .build())
    print('Starting...')

    id_handler = CommandHandler("send_my_id", id_command, )
    stone_handler = CommandHandler("moyai", moyai_command, )
    message_handler = MessageHandler(~filters.COMMAND, message_processing)

    handlers = (id_handler, stone_handler, message_handler)
    application.add_handlers(handlers)

    print('Poling...')
    application.run_polling(poll_interval=5)
