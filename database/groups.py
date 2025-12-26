from .mongodb import groups_col

async def save_group(chat):
    await groups_col.update_one(
        {"chat_id": chat.id},
        {"$set": {
            "chat_id": chat.id,
            "title": chat.title
        }},
        upsert=True
    )

async def count_groups():
    return await groups_col.count_documents({})
