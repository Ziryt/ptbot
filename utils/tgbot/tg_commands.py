import os

from telegram import BotCommandScopeDefault, Update, BotCommand
from telegram.ext import Application, ContextTypes

from utils.ftd.discord_forward import send_sticker, Bot, updates, send_message, send_document

COMMANDS = [BotCommand('send_my_id', '🗿'),
            BotCommand('moyai', '🗿')]


# BotCommand('forward', 'send to discord'),
# BotCommand('sticker', ' send sticker to discord'),
# BotCommand('cancel', 'cancel current command'),


async def set_commands(app: Application):
    bot = app.bot
    await bot.set_my_commands(COMMANDS, scope=BotCommandScopeDefault())


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = f'{user.name}\n {user.link if user.link else "no @"}\n {user.id}'
    await context.bot.send_message(os.getenv('TG_GROUP'), text)


async def moyai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🗿')


async def message_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.sticker:
        await send_sticker(update, context)
        return
    if update.message.document:
        await send_document(update, context)
        return
    received_list = await Bot.get_updates()
    if not updates:
        updates.extend(received_list)
    if update.message.message_id == updates[-1].message.message_id:
        await send_message(updates, context)
        updates.clear()
