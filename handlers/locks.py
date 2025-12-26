from pyrogram import filters
import re

LINK_REGEX = r"(https?://|t\.me/)"

def register_locks(app):

    @app.on_message(filters.group & filters.text)
    async def anti_link(_, message):
        if re.search(LINK_REGEX, message.text.lower()):
            try:
                await message.delete()
            except:
                pass
