from .mongodb import users_col

async def save_user(user):
    await users_col.update_one(
        {"user_id": user.id},
        {"$set": {
            "user_id": user.id,
            "first_name": user.first_name,
            "username": user.username
        }},
        upsert=True
    )

async def count_users():
    return await users_col.count_documents({})
