from emojis import get
from telegram import Update, Message, Bot


async def create_ms(msg: Message, upds: list[Update], bot: Bot):
    ms = MS(msg, upds, bot)
    if msg.forward_from or msg.forward_from_chat:
        await ms.create_op(msg, bot)
    return ms


class MS:
    def __init__(self, msg: Message, upds: list[Update], bot: Bot):
        self.bot = bot
        self.author_name = msg.chat.first_name

        self.op: OriginalPoster = None

        if msg.caption_entities or msg.entities:
            self.entities = msg.caption_entities or msg.entities
            self.enrich_text(msg.caption or msg.text)
        else:
            self.text = msg.caption or msg.text or None

        self.photos = [upd.message.photo[-1] if upd.message.photo else None for upd in upds]
        self.videos = [upd.message.video for upd in upds]

        self.document = msg.document
        self.date = msg.forward_date or None

    async def create_op(self, *args):
        self.op = OriginalPoster(*args)
        await self.op._get_chat()

    def enrich_text(self, text):
        correction = -len(get(text))
        ent_list = self.entities
        for ent in ent_list:
            if ent.url:
                offset = ent.offset + correction
                text = self.put_link(ent.url, offset, ent.length, text)
                correction += 4 + len(ent.url)
        self.text = text

    def put_link(self, url, offset, length, text):
        before = text[:offset]
        if text[offset:][:length].endswith('\n'):
            after = text[offset:][length - 1:]
            wrapped_link = f'[{text[offset:][:length - 1]}]({url})'
        else:
            after = text[offset:][length:]
            wrapped_link = f'[{text[offset:][:length]}]({url})'

        return before + wrapped_link + after


class OriginalPoster:
    def __init__(self, msg: Message, bot: Bot):
        self.msg = msg
        self.bot = bot

    async def _get_chat(self):
        if self.msg.forward_from_chat:
            self.chat = await self.bot.getChat(self.msg.forward_from_chat.id)
            self.name = self.chat.effective_name
        else:
            self.name = self.msg.forward_from.first_name

    @property
    async def chat_url(self):
        if self.chat.photo:
            _ = await self.bot.get_file(self.chat.photo.big_file_id)
            return _.file_path
        else:
            return 'https://wow.zamimg.com/images/wow/icons/large/inv_misc_questionmark.jpg'

