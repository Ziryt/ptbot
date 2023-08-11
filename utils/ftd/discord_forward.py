import io
import os
from typing import Final
from urllib import request

import discord
from discord import SyncWebhook, File, Embed
from telegram import Bot, Update
from telegram.ext import ContextTypes

from utils.ftd.message_serialiazer import MS, Group
from utils.misc.cast_ill import CastIll

THREAD = CastIll(int(os.getenv('TG_THREAD')))

webhook: Final = SyncWebhook.from_url(f'https://discord.com/api/webhooks/{os.getenv("TG_HU")}')
Bot = Bot(os.getenv('TG_TOKEN'))
updates = []


async def send_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = await Bot.get_file(update.message.document.file_id)
    ext = os.path.splitext(doc.file_path)[-1]
    webhook.send(file=File(io.BytesIO(await doc.download_as_bytearray()), filename=f'kek{ext}'), thread=THREAD)


async def send_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = await Bot.get_file(update.message.sticker.file_id)
    ext = os.path.splitext(sticker.file_path)[-1]
    if ext == '.tgs':
        request.urlretrieve(sticker.file_path, "sticker.tgs")
        import subprocess
        subprocess.run([r"venv/Scripts/python.exe", 'call_inc.py'])
        webhook.send(file=File(fp='result.gif'), thread=THREAD)
        os.remove('sticker.tgs')
        os.remove('result.gif')
    else:
        webhook.send(file=File(io.BytesIO(await sticker.download_as_bytearray()), filename=f'kek{ext}'), thread=THREAD)


async def send_message(all_updates: list[Update], context: ContextTypes.DEFAULT_TYPE):
    message = MS(msg=all_updates[0].message, upds=all_updates, bot=Bot)
    await message.set_vars()
    if isinstance(message.op, Group):
        await message.op.set_vars()

    embeds: list[Embed] = [Embed()]
    embeds[0].set_author(name=f'sent by {message.author_name}')
    embeds[0].url = 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg'
    if message.date:
        embeds[0].set_footer(text=message.date)
    if message.op:
        embeds[0].title = message.op.name
        embeds[0].url = message.op.url
        embeds[0].set_thumbnail(url=message.op.profile_pic)
    embeds[0].description = message.text
    if message.photos:
        embeds = await add_photos(embeds, message)
    send(embeds, videos=message.videos, docs=message.document)


async def add_photos(embeds: list[Embed], msg: MS):
    embeds[0].set_image(url=msg.photos[0])
    if len(msg.photos) > 1:
        ext = [discord.Embed(url=msg.op.url).set_image(url=photo_url) for photo_url in msg.photos[1:]]
        embeds.extend(ext)
    return embeds


def send(embeds, videos, docs):
    files = []
    if videos:
        files.extend(videos)
    if docs:
        files.extend(docs)
    if videos or docs:
        webhook.send(files=files, embeds=embeds[:4], thread=THREAD)
    else:
        webhook.send(embeds=embeds[:4], thread=THREAD)
    embeds_tail = embeds[4:]
    while embeds_tail:
        if len(embeds_tail) < 4:
            webhook.send(embeds=embeds_tail, thread=THREAD)
            break
        current = []
        for i in range(4):
            current.append(embeds_tail[0])
            del embeds_tail[0]
        webhook.send(embeds=current, thread=THREAD)
