from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup
from database.filters import add_filter, remove_filter, get_filters
from utils.typing import typing
from utils.buttons import parse_buttons

def register_filters(app):

    # ADD FILTER
    @app.on_message(filters.command("filter") & filters.group)
    async def add(client, message):
        if not message.reply_to_message:
            return await message.reply(
                "Reply to a message (text / media) with:\n"
                "`/filter <keyword>`"
            )

        keyword = message.command[1].lower()
        reply = message.reply_to_message

        data = {
            "chat_id": message.chat.id,
            "keyword": keyword,
            "buttons": None
        }

        # TEXT
        if reply.text:
            data["type"] = "text"
            data["text"] = reply.text
            data["buttons"] = parse_buttons(reply.text)

        # MEDIA
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

        elif reply.sticker:
            data["type"] = "sticker"
            data["file_id"] = reply.sticker.file_id

        else:
            return await message.reply("❌ Unsupported message type.")

        await add_filter(message.chat.id, keyword, data)
        await message.reply(f"✅ Filter `{keyword}` added")

    # REMOVE FILTER
    @app.on_message(filters.command("stop") & filters.group)
    async def stop(_, message):
        keyword = message.command[1].lower()
        await remove_filter(message.chat.id, keyword)
        await message.reply(f"❌ Filter `{keyword}` removed")

    # LIST FILTERS
    @app.on_message(filters.command("filters") & filters.group)
    async def list_filters(_, message):
        items = []
        async for f in await get_filters(message.chat.id):
            items.append(f"• `{f['keyword']}`")
        await message.reply(
            "🧠 **Active Filters**\n\n" + ("\n".join(items) if items else "No filters")
        )

    # WATCH MESSAGES
    @app.on_message(filters.group)
    async def watch(client, message):
        if not message.text:
            return

        text = message.text.lower()
        async for f in await get_filters(message.chat.id):
            if f["keyword"] in text:
                await typing(client, message.chat.id, 1)

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

                elif f["type"] == "sticker":
                    await message.reply_sticker(f["file_id"])

                break
