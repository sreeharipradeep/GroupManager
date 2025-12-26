from database.mongodb import db


COLLECTION = db.filters


async def add_filter(chat_id, keyword, data):
    data["chat_id"] = chat_id
    data["keyword"] = keyword

    await COLLECTION.update_one(
        {"chat_id": chat_id, "keyword": keyword},
        {"$set": data},
        upsert=True
    )


async def remove_filter(chat_id, keyword):
    await COLLECTION.delete_one(
        {"chat_id": chat_id, "keyword": keyword}
    )


async def get_filters(chat_id):
    cursor = COLLECTION.find({"chat_id": chat_id})
    return await cursor.to_list(length=100)
