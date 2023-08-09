import os
from typing import Final
from urllib import request

import discord
import emojis
import telegram
from discord import SyncWebhook, File, Embed
from telegram import Bot, Update
from telegram.ext import ContextTypes

from utils.ftd.message_serialiazer import create_ms, MS, Group
from utils.misc.cast_ill import CastIll

THREAD = CastIll(1124925499748130826)

webhook: Final = SyncWebhook.from_url(f'https://discord.com/api/webhooks/{os.getenv("TG_HUT")}')
Bot = Bot(os.getenv('TG_TOKEN'))
updates = []


async def cool():
    print('🤙🤙🤙')


async def send_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def send_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = await Bot.get_file(update.message.sticker.file_id)
    if sticker.file_path.endswith('.tgs'):
        request.urlretrieve(sticker.file_path, "sticker.tgs")
        import subprocess
        print('converting sticker...')
        subprocess.run([r"venv/Scripts/python.exe", 'call_inc.py'])
        webhook.send(file=File(fp='result.gif'))
        os.remove('sticker.tgs')
        os.remove('result.gif')
    else:
        webhook.send(sticker.file_path)
    await cool()


async def send_message(all_updates: list[Update], context: ContextTypes.DEFAULT_TYPE):
    message = MS(msg=all_updates[0].message, upds=all_updates, bot=Bot)
    await message.set_vars()
    if isinstance(message.op, Group):
        await message.op.set_vars()
    photo_bool = False

    embeds1: list[Embed] = [Embed()]
    embeds1[0].set_author(name=f'sent by {message.author_name}')
    embeds1[0].url = 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg'
    if message.op:
        embeds1[0].title = message.op.name
        embeds1[0].url = message.op.url
        embeds1[0].set_thumbnail(url=message.op.profile_pic)
    embeds1[0].description = message.text
    if message.photos:
        embeds1 = await add_photos(embeds1, message)
    send(embeds1, videos=message.videos)


async def add_photos(embeds: list[Embed], msg: MS):
    embeds[0].set_image(url=msg.photos[0])
    if len(msg.photos) > 1:
        ext = [discord.Embed(url=msg.op.url).set_image(url=photo_url) for photo_url in msg.photos[1:]]
        embeds.extend(ext)
    return embeds


def send(embeds, videos):
    if videos:
        webhook.send(files=videos, embeds=embeds[:4])
    else:
        webhook.send(embeds=embeds[:4])
    embeds_tail = embeds[4:]
    while embeds_tail:
        if len(embeds_tail) < 4:
            webhook.send(embeds=embeds_tail)
            break
        current = []
        for i in range(4):
            current.append(embeds_tail[0])
            del embeds_tail[0]
        webhook.send(embeds=current)


    # reply = all_updates[0].message
    # upd_photos, upd_videos = await get_lists(all_updates)
    # embed_sent = False
    #
    # embeds = [Embed(description=get_text(reply))]
    # embeds[0].set_author(name=f'forwarded by {reply.chat.first_name}')
    #
    # if reply.forward_from or reply.forward_from_chat:
    #     title, title_link = await get_title(reply)
    #     embeds[0].title = title
    #
    # if reply.text or reply.caption:
    #     set_chat_links(reply, embeds)
    # await cool()
    #
    # if upd_photos:
    #     if reply.forward_from or reply.forward_from_chat:
    #         title, title_link = await get_title(reply)
    #         if title_link:
    #             embed_sent = await get_photos(embeds, upd_photos, title_link)
    #         else:
    #             embed_sent = await get_photos(embeds, upd_photos)
    #     else:
    #         embed_sent = await get_photos(embeds, upd_photos)
    #
    # if upd_videos:
    #     if not embed_sent:
    #         webhook.send(embeds=embeds)
    #     await get_videos(upd_videos)
    #
    # if not upd_photos and not upd_videos:
    #     webhook.send(embeds=embeds)


async def get_lists(all_updates):
    photos, videos = [], []
    for upd in all_updates:
        if upd.message.photo:
            photos.append(upd)
        if upd.message.video:
            videos.append(upd)
    return photos, videos


def get_text(reply):
    return reply.text if reply.text else reply.caption


async def get_title(reply):
    if reply.forward_from_chat:
        try:
            chat = await Bot.get_chat(reply.forward_from_chat.id)
            return reply.forward_from_chat.title, chat.link
        except telegram.error.Forbidden:
            return reply.forward_from_chat.title, ''
    else:
        chat = await Bot.get_chat(reply.forward_from.id)
        return reply.forward_from.name, chat.link


def set_chat_links(reply, embeds):
    correction = -len(emojis.get(get_text(reply)))
    ent_list = reply.caption_entities if reply.caption_entities else reply.entities
    for ent in ent_list:
        if ent.url:
            offset = ent.offset + correction
            embeds[0].description = put_link(ent.url, offset, ent.length, embeds[0].description)
            correction += 4 + len(ent.url)


def put_link(url, offset, length, text):
    before = text[:offset]
    after = text[offset:][length:]
    wrapped_link = f'[{text[offset:][:length]}]({url})'
    return before + wrapped_link + after


async def get_photos(embeds, upd_list, link='https://www.youtube.com/watch?v=dQw4w9WgXcQ'):
    await set_photo(upd_list[0], embeds[0], link)
    if len(upd_list) > 1:
        photo_list = []
        for upd in upd_list[1:]:
            pic_info = await Bot.get_file(upd.message.photo[-1].file_id)
            photo_list.append(pic_info.file_path)
        for photo_url in photo_list:
            embed = discord.Embed().set_image(url=photo_url)
            embeds.append(embed)
        for embed in embeds:
            if not embed.url:
                embed.url = link
    while embeds:
        if len(embeds) < 4:
            webhook.send(embeds=embeds)
            break
        current = []
        for i in range(4):
            current.append(embeds.pop(0))
        webhook.send(embeds=current)
    return True


async def set_photo(upd, embed, link):
    pic_info = await Bot.get_file(upd.message.photo[-1].file_id)
    embed.url = link
    embed.set_image(url=pic_info.file_path)


async def get_videos(video_list):
    links = []
    for upd in video_list:
        video_info = await Bot.get_file(upd.message.video.file_id)
        links.append(video_info.file_path)
    x = '\n'.join(links)
    webhook.send(content=x)