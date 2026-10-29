from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from app.routers.auth import get_current_user
from app.db.mongo import get_db
from app.schemas.conversation import CreateConversationRequest, RenameConversationRequest, ConversationResponse, ConversationWithMessagesResponse, MessageResponse

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

def to_conv_response(doc) -> ConversationResponse:
    return ConversationResponse(
        id=str(doc["_id"]),
        user_id=str(doc["user_id"]),
        title=doc["title"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        last_message_at=doc["last_message_at"]
    )

def to_msg_response(doc) -> MessageResponse:
    return MessageResponse(
        id=str(doc["_id"]),
        conversation_id=str(doc["conversation_id"]),
        role=doc["role"],
        content=doc["content"],
        created_at=doc["created_at"]
    )

@router.post("", response_model=ConversationResponse)
async def create_conversation(req: CreateConversationRequest, current_user = Depends(get_current_user)):
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = {
        "user_id": current_user["_id"],
        "title": req.title or "New Chat",
        "created_at": now,
        "updated_at": now,
        "last_message_at": now
    }
    res = await db["conversations"].insert_one(doc)
    doc["_id"] = res.inserted_id
    return to_conv_response(doc)

@router.get("", response_model=list[ConversationResponse])
async def list_conversations(current_user = Depends(get_current_user)):
    db = get_db()
    cursor = db["conversations"].find({"user_id": current_user["_id"]}).sort("last_message_at", -1)
    docs = await cursor.to_list(length=100)
    return [to_conv_response(d) for d in docs]

@router.get("/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation(conversation_id: str, current_user = Depends(get_current_user)):
    db = get_db()
    try:
        oid = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    conv = await db["conversations"].find_one({"_id": oid, "user_id": current_user["_id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = await db["messages"].find({"conversation_id": oid}).sort("created_at", 1).to_list(length=1000)
    return ConversationWithMessagesResponse(
        conversation=to_conv_response(conv),
        messages=[to_msg_response(m) for m in msgs]
    )

@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation(conversation_id: str, req: RenameConversationRequest, current_user = Depends(get_current_user)):
    db = get_db()
    try:
        oid = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
    now = datetime.now(timezone.utc)
    res = await db["conversations"].find_one_and_update(
        {"_id": oid, "user_id": current_user["_id"]},
        {"$set": {"title": req.title.strip(), "updated_at": now}},
        return_document=True
    )
    if not res:
        # need import ReturnDocument
        pass
    conv = await db["conversations"].find_one({"_id": oid, "user_id": current_user["_id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Not found")
    # Actually update again correctly
    await db["conversations"].update_one({"_id": oid}, {"$set": {"title": req.title.strip(), "updated_at": now}})
    conv = await db["conversations"].find_one({"_id": oid})
    return to_conv_response(conv)

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, current_user = Depends(get_current_user)):
    db = get_db()
    try:
        oid = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
    conv = await db["conversations"].find_one({"_id": oid, "user_id": current_user["_id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Not found")
    await db["conversations"].delete_one({"_id": oid})
    await db["messages"].delete_many({"conversation_id": oid})
    return {"message": "Deleted"}
