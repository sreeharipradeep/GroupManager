from .mongodb import db

# Collection
warns_col = db.warns


# =========================
# ADD WARN
# =========================
async def add_warn(chat_id, user_id):
    """
    Increments warn count and returns new count
    """
    result = await warns_col.find_one_and_update(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True
    )

    # If new document
    if not result:
        return 1

    return result.get("count", 1)


# =========================
# RESET WARNS
# =========================
async def reset_warn(chat_id, user_id):
    await warns_col.delete_one(
        {"chat_id": chat_id, "user_id": user_id}
    )


# =========================
# GET WARN COUNT (OPTIONAL)
# =========================
async def get_warn_count(chat_id, user_id):
    data = await warns_col.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )
    return data["count"] if data else 0
