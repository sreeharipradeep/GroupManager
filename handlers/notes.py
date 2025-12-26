from pyrogram import filters
from database.notes import save_note, get_note

def register_notes(app):

    @app.on_message(filters.command("save") & filters.group)
    async def save(_, message):
        name, text = message.text.split(None, 2)[1:]
        await save_note(message.chat.id, name, text)
        await message.reply("💾 Note saved.")

    @app.on_message(filters.command("get") & filters.group)
    async def get(_, message):
        name = message.text.split(None, 1)[1]
        note = await get_note(message.chat.id, name)
        await message.reply(note or "❌ Note not found.")
