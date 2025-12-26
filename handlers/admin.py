from pyrogram import filters
from pyrogram.types import ChatPermissions
from utils.typing import typing


def register_admin(app):

    # =========================
    # Helper: admin check
    # =========================
    async def is_admin(client, chat_id, user_id):
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "owner")

    # =========================
    # BAN
    # =========================
    @app.on_message(filters.command("ban") & filters.group)
    async def ban(client, message):
        if not message.reply_to_message:
            await message.reply("❗ Reply to a user to ban.")
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("❌ You are not an admin.")
            return

        await typing(client, message.chat.id)
        user_id = message.reply_to_message.from_user.id

        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply("🚫 User banned.")

    # =========================
    # UNBAN
    # =========================
    @app.on_message(filters.command("unban") & filters.group)
    async def unban(client, message):
        if not message.reply_to_message:
            await message.reply("❗ Reply to a user to unban.")
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("❌ You are not an admin.")
            return

        user_id = message.reply_to_message.from_user.id
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply("✅ User unbanned.")

    # =========================
    # MUTE
    # =========================
    @app.on_message(filters.command("mute") & filters.group)
    async def mute(client, message):
        if not message.reply_to_message:
            await message.reply("❗ Reply to a user to mute.")
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("❌ You are not an admin.")
            return

        await typing(client, message.chat.id)
        user_id = message.reply_to_message.from_user.id

        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions()
        )
        await message.reply("🔇 User muted.")

    # =========================
    # UNMUTE
    # =========================
    @app.on_message(filters.command("unmute") & filters.group)
    async def unmute(client, message):
        if not message.reply_to_message:
            await message.reply("❗ Reply to a user to unmute.")
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("❌ You are not an admin.")
            return

        user_id = message.reply_to_message.from_user.id

        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await message.reply("🔊 User unmuted.")

    # =========================
    # PURGE
    # =========================
    @app.on_message(filters.command("purge") & filters.group)
    async def purge(client, message):
        if not message.reply_to_message:
            await message.reply("❗ Reply to a message to start purge.")
            return

        if not await is_admin(client, message.chat.id, message.from_user.id):
            await message.reply("❌ You are not an admin.")
            return

        start = message.reply_to_message.id
        end = message.id

        message_ids = list(range(start, end + 1))

        await client.delete_messages(
            chat_id=message.chat.id,
            message_ids=message_ids
        )
