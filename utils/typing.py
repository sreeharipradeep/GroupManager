import asyncio
from pyrogram.enums import ChatAction

async def typing(client, chat_id, seconds=2):
    await client.send_chat_action(chat_id, ChatAction.TYPING)
    await asyncio.sleep(seconds)
