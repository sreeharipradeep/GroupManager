from pyrogram import filters
from utils.typing import typing

def register_admin(app):

    @app.on_message(filters.command("ban") & filters.group)
    async def ban(client, message):
        if not message.reply_to_message:
            return
        await typing(client, message.chat.id)
        await message.chat.ban_member(message.reply_to_message.from_user.id)
        await message.reply("🚫 Banned.")

    @app.on_message(filters.command("mute") & filters.group)
    async def mute(client, message):
        if not message.reply_to_message:
            return
        await typing(client, message.chat.id)
        await message.chat.restrict_member(
            message.reply_to_message.from_user.id,
            permissions={}
        )
        await message.reply("🔇 Muted.")

    @app.on_message(filters.command("purge") & filters.group)
    async def purge(_, message):
        if not message.reply_to_message:
            return
        ids = range(message.reply_to_message.id, message.id)
        for i in ids:
            try:
                await message.chat.delete_messages(i)
            except:
                pass
