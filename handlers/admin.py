from pyrogram import filters
from pyrogram.types import ChatPermissions
from utils.admin import is_admin
from utils.typing import typing
from database.warns import (
    remove_one_warn,
    add_warn,
    get_warn_count
)

# =========================
# DEFAULT WARN LIMIT
# =========================
DEFAULT_WARN_LIMIT = 3
WARN_LIMITS = {}  # per-group (memory)


def register_admin(app):

    # =========================
    # HELPER: RESOLVE TARGET USER
    # =========================
    async def get_target_user(client, message):
        # Reply based
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user

        # Mention / username based
        if len(message.command) >= 2:
            try:
                return await client.get_users(message.command[1])
            except:
                return None

        return None

    # =========================
    # HELPER: PARSE REASON
    # =========================
    def parse_reason(message, start_index):
        if len(message.command) > start_index:
            return " ".join(message.command[start_index:])
        return None

    # =========================
    # SET WARN LIMIT
    # =========================
    @app.on_message(filters.command("warnlimit") & filters.group)
    async def set_warn_limit(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if len(message.command) < 2 or not message.command[1].isdigit():
            return await message.reply("❗ Usage: `/warnlimit <number>`")

        limit = int(message.command[1])
        WARN_LIMITS[message.chat.id] = limit
        await message.reply(f"⚠️ Warn limit set to **{limit}**")

    # =========================
    # WARN USER
    # =========================
    @app.on_message(filters.command("warn") & filters.group)
    async def warn_user(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply(
                "❗ Reply to a user or use:\n`/warn <username> <reason>`"
            )

        # Prevent warning admins
        member = await client.get_chat_member(message.chat.id, user.id)
        if member.status in ("administrator", "owner"):
            return await message.reply("❌ You can't warn admins.")

        reason = (
            parse_reason(message, 1)
            if message.reply_to_message
            else parse_reason(message, 2)
        )

        await typing(client, message.chat.id, 1)

        count = await add_warn(message.chat.id, user.id)
        limit = WARN_LIMITS.get(message.chat.id, DEFAULT_WARN_LIMIT)

        if count >= limit:
            try:
                await client.ban_chat_member(message.chat.id, user.id)
                await reset_warn(message.chat.id, user.id)
                await message.reply(
                    f"🚫 {user.mention} banned (warn limit {limit})."
                )
            except Exception as e:
                await message.reply(f"❌ Ban failed: `{e}`")
        else:
            text = f"⚠️ {user.mention} warned ({count}/{limit})"
            if reason:
                text += f"\n📝 Reason: {reason}"
            await message.reply(text)

    # =========================
    # REMOVE ONE WARN
    # =========================
@app.on_message(filters.command("rmwarn") & filters.group)
async def remove_warn(client, message):
    if not await is_admin(client, message):
        return await message.reply("❌ Admins only.")

    user = await get_target_user(client, message)
    if not user:
        return await message.reply(
            "❗ Reply to a user or use:\n`/rmwarn <username>`"
        )

    new_count = await remove_one_warn(message.chat.id, user.id)

    await message.reply(
        f"✅ One warn removed from {user.mention}\n"
        f"⚠️ Current warns: **{new_count}**"
    )
    # =========================
    # SHOW WARNINGS
    # =========================
    @app.on_message(filters.command("warnings") & filters.group)
    async def show_warnings(client, message):
        user = await get_target_user(client, message)
        if not user:
            return await message.reply(
                "❗ Reply to a user or use:\n`/warnings <username>`"
            )

        count = await get_warn_count(message.chat.id, user.id)
        await message.reply(f"⚠️ {user.mention} has **{count}** warning(s).")

    # =========================
    # BAN USER
    # =========================
    @app.on_message(filters.command("ban") & filters.group)
    async def ban_user(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        reason = (
            parse_reason(message, 1)
            if message.reply_to_message
            else parse_reason(message, 2)
        )

        try:
            await client.ban_chat_member(message.chat.id, user.id)
            text = f"🚫 {user.mention} banned."
            if reason:
                text += f"\n📝 Reason: {reason}"
            await message.reply(text)
        except Exception as e:
            await message.reply(f"❌ Ban failed: `{e}`")

    # =========================
    # UNBAN USER
    # =========================
    @app.on_message(filters.command("unban") & filters.group)
    async def unban_user(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        await client.unban_chat_member(message.chat.id, user.id)
        await message.reply(f"✅ {user.mention} unbanned.")

    # =========================
    # MUTE USER (RESTRICTIONS)
    # =========================
    @app.on_message(filters.command("mute") & filters.group)
    async def mute_user(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        reason = (
            parse_reason(message, 1)
            if message.reply_to_message
            else parse_reason(message, 2)
        )

        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )

        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions
        )

        text = f"🔇 {user.mention} muted."
        if reason:
            text += f"\n📝 Reason: {reason}"
        await message.reply(text)

    # =========================
    # UNMUTE USER
    # =========================
    @app.on_message(filters.command("unmute") & filters.group)
    async def unmute_user(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        user = await get_target_user(client, message)
        if not user:
            return await message.reply("❗ Reply or mention a user.")

        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )

        await client.restrict_chat_member(
            message.chat.id,
            user.id,
            permissions
        )

        await message.reply(f"🔊 {user.mention} unmuted.")

    # =========================
    # PIN MESSAGE
    # =========================
    @app.on_message(filters.command("pin") & filters.group)
    async def pin_message(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply("❗ Reply to a message to pin.")

        await client.pin_chat_message(
            message.chat.id,
            message.reply_to_message.id
        )
        await message.reply("📌 Message pinned.")

    # =========================
    # PURGE (REPLY-BASED)
    # =========================
    @app.on_message(filters.command("purge") & filters.group)
    async def purge_messages(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply("❗ Reply to a message to start purge.")

        start_id = message.reply_to_message.id
        end_id = message.id

        for msg_id in range(start_id, end_id + 1):
            try:
                await client.delete_messages(message.chat.id, msg_id)
            except:
                pass

        await message.reply("🧹 Purge completed.")
