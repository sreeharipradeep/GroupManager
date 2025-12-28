from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from utils.admin import is_admin
from utils.typing import typing
from utils.buttons import parse_buttons
from database.filters import (
    add_filter,
    remove_filter,
    get_filters,
    remove_all_filters
)


def build_buttons(raw_buttons):
    """
    Convert raw DB buttons → InlineKeyboardMarkup
    """
    if not raw_buttons:
        return None

    keyboard = []
    for row in raw_buttons:
        btn_row = []
        for btn in row:
            if "url" in btn:
                btn_row.append(
                    InlineKeyboardButton(
                        btn["text"],
                        url=btn["url"]
                    )
                )
            elif "callback_data" in btn:
                btn_row.append(
                    InlineKeyboardButton(
                        btn["text"],
                        callback_data=btn["callback_data"]
                    )
                )
        if btn_row:
            keyboard.append(btn_row)

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
            return await message.reply("❗ Reply to a message.")

        admin_only = False

        if message.command[1] == "-admin":
            admin_only = True
            keyword = message.command[2].lower()
        else:
            keyword = message.command[1].lower()

        reply = message.reply_to_message

        data = {
            "chat_id": message.chat.id,
            "keyword": keyword,
            "admin_only": admin_only
        }

        if reply.text:
            data["type"] = "text"
            data["text"] = reply.text
            data["buttons"] = parse_buttons(reply.text)

        elif reply.photo:
            data["type"] = "photo"
            data["file_id"] = reply.photo.file_id
            data["caption"] = reply.caption
            data["buttons"] = parse_buttons(reply.caption or "")

        elif reply.video:
            data["type"] = "video"
            data["file_id"] = reply.video.file_id
            data["caption"] = reply.caption
            data["buttons"] = parse_buttons(reply.caption or "")

        else:
            return await message.reply("❌ Unsupported message type.")

        await add_filter(message.chat.id, keyword, data)
        await message.reply(f"✅ Filter `{keyword}` added!")

    # =========================
    # STOP FILTER
    # =========================
    @app.on_message(filters.command("stop") & filters.group)
    async def stop(_, message):
        await remove_filter(message.chat.id, message.command[1].lower())
        await message.reply("❌ Filter removed.")

    # =========================
    # STOP ALL
    # =========================
    @app.on_message(filters.command("stopall") & filters.group)
    async def stopall(_, message):
        await remove_all_filters(message.chat.id)
        await message.reply("🧹 All filters removed.")

    # =========================
    # LIST FILTERS  ✅ (THIS WAS MISSING)
    # =========================
    @app.on_message(filters.command("filters") & filters.group)
    async def list_filters_cmd(client, message):
        filters_list = await get_filters(message.chat.id)

        if not filters_list:
            return await message.reply("🧠 No active filters in this group.")

        text = "🧠 **Active Filters**\n\n"
        for f in filters_list:
            badge = " 🔐" if f.get("admin_only") else ""
            text += f"• `{f['keyword']}`{badge}\n"

        await message.reply(text)
        
    # =========================
    # WATCH MESSAGES
    # =========================
    @app.on_message(filters.group & (filters.text | filters.caption), group=10)
    async def watch(client, message):

        text = (message.text or message.caption or "").lower()
        words = text.split()

        filters_list = await get_filters(message.chat.id)
        if not filters_list:
            return

        for f in filters_list:
            if f["keyword"] in words:

                if f.get("admin_only") and not await is_admin(client, message):
                    continue

                await typing(client, message.chat.id)

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

                break
