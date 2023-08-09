import io

import discord
import telegram.error
from emojis import get
from telegram import Update, Message, Bot, File


class MS:
    def __init__(self, msg: Message, upds: list[Update], bot: Bot):
        self.msg = msg
        self.upds = upds
        self.bot = bot
        self.author_name = msg.chat.first_name

        self.op = None
        if msg.forward_from_chat:
            self.op = Group(self.msg, self.bot)
        if msg.forward_from:
            self.op = OriginalPoster(self.msg)

        if msg.caption_entities or msg.entities:
            self.entities = msg.caption_entities or msg.entities
            self.enrich_text(msg.caption or msg.text)
        else:
            self.text = msg.caption or msg.text or None

        self.photos = None
        self.videos = None

        self.document = msg.document
        self.date = msg.forward_date.strftime(f'%H:%M\n%d %B, %Y ') or None

    def enrich_text(self, text):
        correction = -len(get(text))
        ent_list = self.entities
        for ent in ent_list:
            if ent.url:
                offset = ent.offset + correction
                text = self._put_link(ent.url, offset, ent.length, text)
                correction += 4 + len(ent.url)
        self.text = text

    @staticmethod
    def _put_link(url, offset, length, text):
        before = text[:offset]
        if text[offset:][:length].endswith('\n'):
            after = text[offset:][length - 1:]
            wrapped_link = f'[{text[offset:][:length - 1]}]({url})'
        else:
            after = text[offset:][length:]
            wrapped_link = f'[{text[offset:][:length]}]({url})'
        return before + wrapped_link + after

    async def set_vars(self):
        if any(upd.message.photo is not None for upd in self.upds):
            photos = [await self.bot.get_file(upd.message.photo[-1].file_id)
                      for upd in self.upds if upd.message.photo]
            # Cam potentially vanish
            self.photos = [photo.file_path for photo in photos]

        if any(upd.message.video is not None for upd in self.upds):
            video_files: list[File] = [await self.bot.get_file(upd.message.video.file_id)
                                       for upd in self.upds if upd.message.video]
            video_bytes = [await video.download_as_bytearray() for video in video_files]
            self.videos = [discord.File(io.BytesIO(byte), filename=f"attch{i + 1}.mp4")
                           for i, byte in enumerate(video_bytes)]


class OriginalPoster:
    def __init__(self, msg: Message):
        self.msg = msg
        self.name = msg.forward_from.first_name
        self.url = 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg'
        self.profile_pic = 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg'


class Group:
    def __init__(self, msg: Message, bot: Bot):
        self.chat = None
        self.name = None
        self.url = None
        self.profile_pic = None
        self.msg = msg
        self.bot = bot

    async def set_vars(self):
        self.profile_pic = 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg'
        try:
            self.chat = await self.bot.getChat(self.msg.forward_from_chat.id)
            # Cam potentially vanish
            if self.chat.photo:
                profile_pic = await self.bot.get_file(self.chat.photo.big_file_id)
                self.profile_pic = profile_pic.file_path
        except telegram.error.Forbidden:
            pass
        self.name = self.msg.forward_from_chat.effective_name
        self.url = self.msg.forward_from_chat.link

