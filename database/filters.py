from .mongodb import db

filters_col = db["filters"]

async def add_filter(chat_id, keyword, reply):
    await filters_col.update_one(
        {"chat_id": chat_id, "keyword": keyword},
        {"$set": {"reply": reply}},
        upsert=True
    )

async def remove_filter(chat_id, keyword):
    await filters_col.delete_one({"chat_id": chat_id, "keyword": keyword})

async def get_filters(chat_id):
    return filters_col.find({"chat_id": chat_id})
