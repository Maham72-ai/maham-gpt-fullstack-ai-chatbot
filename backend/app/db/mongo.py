from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    # indexes
    await db["users"].create_index("email", unique=True)
    await db["conversations"].create_index([("user_id", 1), ("last_message_at", -1)])
    await db["messages"].create_index([("conversation_id", 1), ("created_at", 1)])
    print("MongoDB connected")

async def close_mongo_connection():
    global client
    if client:
        client.close()

def get_db():
    return db
