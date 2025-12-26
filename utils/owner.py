from pyrogram import filters
from config import OWNER_ID
from database.users import count_users
from database.groups import count_groups
from database.mongodb import users_col
from utils.typing import typing

def register_owner(app):

    @app.on_message(filters.command("stats") & filters.user(OWNER_ID))
    async def stats(client, message):
        await typing(client, message.chat.id)
        users = await count_users()
        groups = await count_groups()
        await message.reply_text(
            f"📊 **Bot Statistics**\n\n"
            f"👤 Users : `{users}`\n"
            f"👥 Groups : `{groups}`"
        )

    @app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
    async def broadcast(client, message):
        if not message.reply_to_message:
            return await message.reply("Reply to a message to broadcast.")

        sent = failed = 0
        async for user in users_col.find({}):
            try:
                await message.reply_to_message.copy(user["user_id"])
                sent += 1
            except:
                failed += 1

        await message.reply_text(
            f"📢 **Broadcast Done**\n\n"
            f"✅ Sent: `{sent}`\n"
            f"❌ Failed: `{failed}`"
        )
