from pyrogram import filters
from pyrogram.types import CallbackQuery
from utils.admin import is_admin
from utils.typing import typing
from utils.buttons import parse_buttons
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
                "`/filter <keyword>`\n"
                "`/filter -admin <keyword>`"
            )

        admin_only = False

        if len(message.command) < 2:
            return await message.reply("❗ Usage: /filter <keyword>")

        if message.command[1] == "-admin":
            if len(message.command) < 3:
                return await message.reply("❗ Usage: /filter -admin <keyword>")
            admin_only = True
            keyword = message.command[2].lower()
        else:
            keyword = message.command[1].lower()

        reply = message.reply_to_message

        data = {
            "chat_id": message.chat.id,
            "keyword": keyword,
            "admin_only": admin_only,
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

        lock = " 🔐" if admin_only else ""
        await message.reply(f"✅ Filter `{keyword}` added{lock}!")

    # =========================
    # REMOVE SINGLE FILTER
    # =========================
    @app.on_message(filters.command(["stop", "stopfilter"]) & filters.group)
    async def stop_filter(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        if len(message.command) < 2:
            return await message.reply("❗ Usage: /stop <keyword>")

        keyword = message.command[1].lower()
        await remove_filter(message.chat.id, keyword)
        await message.reply(f"❌ Filter `{keyword}` removed.")

    # =========================
    # STOP ALL FILTERS
    # =========================
    @app.on_message(filters.command("stopall") & filters.group)
    async def stop_all_filters(client, message):
        if not await is_admin(client, message):
            return await message.reply("❌ Admins only.")

        await remove_all_filters(message.chat.id)
        await message.reply("🧹 All filters removed from this group.")

    # =========================
    # LIST FILTERS
    # =========================
    @app.on_message(filters.command("filters") & filters.group)
    async def list_filters(client, message):
        data = await get_filters(message.chat.id)

        if not data:
            return await message.reply("🧠 No active filters.")

        text = "🧠 **Active Filters**\n\n"
        for f in data:
            badge = " 🔐" if f.get("admin_only") else ""
            text += f"• `{f['keyword']}`{badge}\n"

        await message.reply(text)

    # =========================
    # WATCH TEXT / CAPTION
    # =========================
    @app.on_message(
        filters.group & (filters.text | filters.caption) & ~filters.regex(r"^/"),
        group=10
    )
    async def watch_messages(client, message):

        text = message.text or message.caption or ""

        # include inline button text
        if message.reply_markup and message.reply_markup.inline_keyboard:
            for row in message.reply_markup.inline_keyboard:
                for btn in row:
                    if btn.text:
                        text += f" {btn.text.lower()}"

        words = text.lower().split()
        filters_list = await get_filters(message.chat.id)
        if not filters_list:
            return

        for f in filters_list:
            if f["keyword"] in words:

                if f.get("admin_only"):
                    if not await is_admin(client, message):
                        continue

                await typing(client, message.chat.id, 1)

                try:
                    if f["type"] == "text":
                        await message.reply(
                            f["text"],
                            reply_markup=f.get("buttons")
                        )

                    elif f["type"] == "photo":
                        await message.reply_photo(
                            f["file_id"],
                            caption=f.get("caption"),
                            reply_markup=f.get("buttons")
                        )

                    elif f["type"] == "video":
                        await message.reply_video(
                            f["file_id"],
                            caption=f.get("caption"),
                            reply_markup=f.get("buttons")
                        )

                    elif f["type"] == "animation":
                        await message.reply_animation(
                            f["file_id"],
                            caption=f.get("caption"),
                            reply_markup=f.get("buttons")
                        )

                    elif f["type"] == "sticker":
                        await message.reply_sticker(f["file_id"])

                except Exception as e:
                    print("Filter send error:", e)

                break

    # =========================
    # WATCH INLINE BUTTON CLICKS
    # =========================
    @app.on_callback_query()
    async def watch_buttons(client, callback: CallbackQuery):

        if not callback.data or not callback.message:
            return

        words = callback.data.lower().split()
        chat_id = callback.message.chat.id

        filters_list = await get_filters(chat_id)
        if not filters_list:
            return

        for f in filters_list:
            if f["keyword"] in words:

                if f.get("admin_only"):
                    fake_msg = callback.message
                    fake_msg.from_user = callback.from_user
                    fake_msg.sender_chat = None
                    if not await is_admin(client, fake_msg):
                        continue

                await typing(client, chat_id, 1)

                try:
                    if f["type"] == "text":
                        await callback.message.reply(
                            f["text"],
                            reply_markup=f.get("buttons")
                        )

                    elif f["type"] == "photo":
                        await callback.message.reply_photo(
                            f["file_id"],
                            caption=f.get("caption"),
                            reply_markup=f.get("buttons")
                        )

                    elif f["type"] == "video":
                        await callback.message.reply_video(
                            f["file_id"],
                            caption=f.get("caption"),
                            reply_markup=f.get("buttons")
                        )

                    elif f["type"] == "animation":
                        await callback.message.reply_animation(
                            f["file_id"],
                            caption=f.get("caption"),
                            reply_markup=f.get("buttons")
                        )

                    elif f["type"] == "sticker":
                        await callback.message.reply_sticker(f["file_id"])

                except Exception as e:
                    print("Callback filter error:", e)

                break
