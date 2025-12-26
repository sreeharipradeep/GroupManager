from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

mongo = AsyncIOMotorClient(MONGO_URI)
db = mongo["rose_clone"]

users_col = db["users"]
groups_col = db["groups"]
