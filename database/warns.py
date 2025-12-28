from .mongodb import db

warns_col = db.warns


# =========================
# ADD WARN (+1)
# =========================
async def add_warn(chat_id, user_id):
    data = await warns_col.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )

    if data:
        new_count = data.get("count", 0) + 1
        await warns_col.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"count": new_count}}
        )
        return new_count
    else:
        await warns_col.insert_one(
            {"chat_id": chat_id, "user_id": user_id, "count": 1}
        )
        return 1


# =========================
# GET WARN COUNT
# =========================
async def get_warn_count(chat_id, user_id):
    data = await warns_col.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )
    return data["count"] if data else 0


# =========================
# REMOVE ONE WARN (-1)
# =========================
async def remove_one_warn(chat_id, user_id):
    data = await warns_col.find_one(
        {"chat_id": chat_id, "user_id": user_id}
    )

    if not data:
        return 0

    count = data.get("count", 0)

    if count <= 1:
        await warns_col.delete_one(
            {"chat_id": chat_id, "user_id": user_id}
        )
        return 0
    else:
        await warns_col.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"count": count - 1}}
        )
        return count - 1


# =========================
# RESET ALL WARNS
# =========================
async def reset_warn(chat_id, user_id):
    await warns_col.delete_one(
        {"chat_id": chat_id, "user_id": user_id}
    )
