from .mongodb import db

warns = db["warns"]

async def add_warn(chat_id, user_id):
    data = await warns.find_one({"chat_id": chat_id, "user_id": user_id})
    count = data["count"] + 1 if data else 1
    await warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": count}},
        upsert=True
    )
    return count

async def reset_warn(chat_id, user_id):
    await warns.delete_one({"chat_id": chat_id, "user_id": user_id})
