from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.admin import is_admin
from utils.typing import typing
from database.filters import (
    add_filter,
    remove_filter,
    remove_all_filters,
    get_filters
)
from utils.buttons import parse_buttons


def build_buttons(buttons):
    """
    buttons format:
    [
      {"text": "Join Now", "url": "https://t.me/jb_links"}
    ]
    """
    if not buttons:
        return None

    keyboard = []
    for btn in buttons:
        if isinstance(btn, dict):
            keyboard.append(
                [InlineKeyboardButton(btn["text"], url=btn["url"])]
            )

    return InlineKeyboardMarkup(keyboard) if keyboard else None


def register_filters(app):

    # =========================
    # ADD FILTER
    # =========================
    @app.on_message(filters.command("filter") & filters.group)
    async def add(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply(
                "❗ Reply to a message with:\n`/filter <keyword>`"
            )

        if len(message.command) < 2:
            return await message.reply("❗ Usage: /filter <keyword>")

        keyword = message.command[1].lower()
        reply = message.reply_to_message

        data = {
            "chat_id": message.chat.id,
            "keyword": keyword,
            "admin_only": False,
            "buttons": []
        }

        # TEXT
        if reply.text:
            data["type"] = "text"
            data["text"] = reply.text
            data["buttons"] = parse_buttons(reply.text)

        # PHOTO
        elif reply.photo:
            data["type"] = "photo"
            data["file_id"] = reply.photo.file_id
            data["caption"] = reply.caption
            data["buttons"] = parse_buttons(reply.caption or "")

        # VIDEO
        elif reply.video:
            data["type"] = "video"
            data["file_id"] = reply.video.file_id
            data["caption"] = reply.caption
            data["buttons"] = parse_buttons(reply.caption or "")

        # STICKER
        elif reply.sticker:
            data["type"] = "sticker"
            data["file_id"] = reply.sticker.file_id

        else:
            return await message.reply("❌ Unsupported message type.")

        await add_filter(message.chat.id, keyword, data)
        await message.reply(f"✅ Filter `{keyword}` added.")

    # =========================
    # REMOVE FILTER
    # =========================
    @app.on_message(filters.command("stop") & filters.group)
    async def stop(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if len(message.command) < 2:
            return await message.reply("❗ Usage: /stop <keyword>")

        keyword = message.command[1].lower()
        await remove_filter(message.chat.id, keyword)
        await message.reply(f"❌ Filter `{keyword}` removed.")

    # =========================
    # STOP ALL
    # =========================
    @app.on_message(filters.command("stopall") & filters.group)
    async def stopall(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        await remove_all_filters(message.chat.id)
        await message.reply("🧹 All filters removed.")

    # =========================
    # LIST FILTERS
    # =========================
    @app.on_message(filters.command("filters") & filters.group)
    async def list_filters(client, message):
        filters_list = await get_filters(message.chat.id)

        if not filters_list:
            return await message.reply("🧠 No active filters.")

        text = "🧠 **Active Filters**\n\n"
        for f in filters_list:
            text += f"• `{f['keyword']}`\n"

        await message.reply(text)

    # =========================
    # WATCH MESSAGES
    # =========================
    @app.on_message(filters.group & filters.text & ~filters.command([]))
    async def watch(client, message):
        text = message.text.lower()

        filters_list = await get_filters(message.chat.id)
        if not filters_list:
            return

        for f in filters_list:
            if f["keyword"] in text.split():

                if f.get("admin_only") and not await is_admin(client, message):
                    continue

                await typing(client, message.chat.id, 1)

                markup = build_buttons(f.get("buttons"))

                if f["type"] == "text":
                    await message.reply(f["text"], reply_markup=markup)

                elif f["type"] == "photo":
                    await message.reply_photo(
                        f["file_id"],
                        caption=f.get("caption"),
                        reply_markup=markup
                    )

                elif f["type"] == "video":
                    await message.reply_video(
                        f["file_id"],
                        caption=f.get("caption"),
                        reply_markup=markup
                    )

                elif f["type"] == "sticker":
                    await message.reply_sticker(f["file_id"])

                break
