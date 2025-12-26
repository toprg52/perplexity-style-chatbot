import os
import motor.motor_asyncio
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.perplexity_clone
sessions_collection = db.get_collection("sessions")

# Helper to format session
def session_helper(session) -> dict:
    return {
        "id": str(session["_id"]),
        "title": session.get("title", "New Chat"),
        "created_at": session.get("created_at"),
        "messages": session.get("messages", [])
    }

async def create_session(session_data: dict) -> dict:
    session = await sessions_collection.insert_one(session_data)
    new_session = await sessions_collection.find_one({"_id": session.inserted_id})
    return session_helper(new_session)

async def get_sessions():
    sessions = []
    async for session in sessions_collection.find().sort("created_at", -1).limit(20):
        sessions.append(session_helper(session))
    return sessions

async def get_session(id: str):
    try:
        session = await sessions_collection.find_one({"_id": ObjectId(id)})
        if session:
            return session_helper(session)
    except:
        pass
    return None

async def add_message(id: str, message: dict):
    try:
        await sessions_collection.update_one(
            {"_id": ObjectId(id)},
            {"$push": {"messages": message}}
        )
        return True
    except:
        return False

async def update_session_title(id: str, title: str):
    try:
        await sessions_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"title": title}}
        )
        return True
    except:
        return False

async def delete_session(id: str):
    try:
        result = await sessions_collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    except:
        return False
