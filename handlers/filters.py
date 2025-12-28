from pyrogram import filters
from pyrogram.types import CallbackQuery
from utils.admin import is_admin
from utils.typing import typing
from utils.buttons import parse_buttons, build_keyboard
from database.filters import (
    add_filter,
    remove_filter,
    remove_all_filters,
    get_filters
)


def register_filters(app):

    # =========================
    # ADD FILTER
    # =========================
    @app.on_message(filters.command("filter") & filters.group)
    async def add_filter_cmd(client, message):

        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if not message.reply_to_message:
            return await message.reply(
                "❗ Reply to a message with:\n"
                "`/filter <keyword>`"
            )

        if len(message.command) < 2:
            return await message.reply("❗ Usage: /filter <keyword>")

        keyword = message.command[1].lower()
        reply = message.reply_to_message

        data = {
            "chat_id": message.chat.id,
            "keyword": keyword,
            "admin_only": False,
            "buttons": None
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

        elif reply.animation:
            data["type"] = "animation"
            data["file_id"] = reply.animation.file_id
            data["caption"] = reply.caption
            data["buttons"] = parse_buttons(reply.caption or "")

        elif reply.sticker:
            data["type"] = "sticker"
            data["file_id"] = reply.sticker.file_id

        else:
            return await message.reply("❌ Unsupported message type.")

        await add_filter(message.chat.id, keyword, data)
        await message.reply(f"✅ Filter `{keyword}` added!")

    # =========================
    # STOP FILTER
    # =========================
    @app.on_message(filters.command("stop") & filters.group)
    async def stop_filter_cmd(client, message):
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
    async def stop_all_filters(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        await remove_all_filters(message.chat.id)
        await message.reply("🧹 All filters removed.")

    # =========================
    # WATCH TEXT
    # =========================
    @app.on_message(
        filters.group & (filters.text | filters.caption) & ~filters.regex(r"^/"),
        group=10
    )
    async def watch_filters(client, message):

        text = (message.text or message.caption or "").lower().split()
        filters_list = await get_filters(message.chat.id)

        for f in filters_list:
            if f["keyword"] in text:

                await typing(client, message.chat.id, 1)
                keyboard = build_keyboard(f.get("buttons"))

                try:
                    if f["type"] == "text":
                        await message.reply(
                            f["text"],
                            reply_markup=keyboard
                        )

                    elif f["type"] == "photo":
                        await message.reply_photo(
                            f["file_id"],
                            caption=f.get("caption"),
                            reply_markup=keyboard
                        )

                    elif f["type"] == "video":
                        await message.reply_video(
                            f["file_id"],
                            caption=f.get("caption"),
                            reply_markup=keyboard
                        )

                    elif f["type"] == "animation":
                        await message.reply_animation(
                            f["file_id"],
                            caption=f.get("caption"),
                            reply_markup=keyboard
                        )

                    elif f["type"] == "sticker":
                        await message.reply_sticker(f["file_id"])

                except Exception as e:
                    print("Filter send error:", e)

                break
