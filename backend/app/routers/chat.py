from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from app.routers.auth import get_current_user
from app.db.mongo import get_db
from app.schemas.conversation import SendMessageRequest, SendMessageResponse, MessageResponse
from app.services.rag_service import retrieve_context, generate_llm_response

router = APIRouter(prefix="/api/conversations", tags=["chat"])

def to_msg(doc) -> MessageResponse:
    return MessageResponse(
        id=str(doc["_id"]),
        conversation_id=str(doc["conversation_id"]),
        role=doc["role"],
        content=doc["content"],
        created_at=doc["created_at"]
    )

@router.post("/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(conversation_id: str, req: SendMessageRequest, current_user = Depends(get_current_user)):
    db = get_db()
    try:
        oid = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    conv = await db["conversations"].find_one({"_id": oid, "user_id": current_user["_id"]})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    now = datetime.now(timezone.utc)
    # save user message
    user_msg_doc = {
        "conversation_id": oid,
        "user_id": current_user["_id"],
        "role": "user",
        "content": req.content,
        "created_at": now
    }
    ures = await db["messages"].insert_one(user_msg_doc)
    user_msg_doc["_id"] = ures.inserted_id

    # auto title from first message
    if conv["title"] == "New Chat":
        title = req.content.strip()[:60]
        await db["conversations"].update_one({"_id": oid}, {"$set": {"title": title}})

    # history for LLM
    history_docs = await db["messages"].find({"conversation_id": oid}).sort("created_at", 1).to_list(length=20)
    history = [{"role": m["role"], "content": m["content"]} for m in history_docs]

    # RAG retrieve
    try:
        context = await retrieve_context(req.content, top_k=3)
    except Exception:
        context = []

    # generate
    try:
        assistant_text = await generate_llm_response(req.content, context, history)
    except Exception as e:
        # preserve user message, return error
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    # save assistant message
    assistant_doc = {
        "conversation_id": oid,
        "user_id": current_user["_id"],
        "role": "assistant",
        "content": assistant_text,
        "created_at": datetime.now(timezone.utc),
        "retrieval_metadata": context
    }
    ares = await db["messages"].insert_one(assistant_doc)
    assistant_doc["_id"] = ares.inserted_id

    # update last_message_at
    await db["conversations"].update_one({"_id": oid}, {"$set": {"last_message_at": assistant_doc["created_at"], "updated_at": assistant_doc["created_at"]}})

    return SendMessageResponse(
        user_message=to_msg(user_msg_doc),
        assistant_message=to_msg(assistant_doc),
        retrieved_context=context
    )
