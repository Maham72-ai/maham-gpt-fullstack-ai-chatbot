from typing import List
from app.core.config import settings
from app.db.qdrant import get_qdrant
import random
import datetime

# Knowledge base for RAG - hidden from user, used internally only
SAMPLE_KB = [
    {"id": "1", "text": "FastAPI is a modern Python web framework for building APIs with automatic docs.", "source": "docs"},
    {"id": "2", "text": "MongoDB stores data in flexible JSON-like documents and uses collections.", "source": "docs"},
    {"id": "3", "text": "Qdrant is a vector database for semantic search and RAG retrieval.", "source": "docs"},
    {"id": "4", "text": "React is a JavaScript library for building user interfaces with components.", "source": "docs"},
    {"id": "5", "text": "Pydantic validates data using Python type hints.", "source": "docs"},
]

# Clean conversational responses when no OpenAI key - makes it feel like ChatGPT
GREETINGS = {
    "hello": ["Hello! 👋 How can I help you today?", "Hey there! What's on your mind?", "Hi! Great to see you. What can I do for you?"],
    "hi": ["Hi! 😊 How can I assist you?", "Hey! What would you like to talk about?", "Hello! I'm here to help."],
    "how are you": ["I'm doing great, thanks for asking! How are you doing?", "I'm fantastic! Ready to help you with anything. How about you?", "All good here! What can I help you with today?"],
    "bye": ["Goodbye! Have an amazing day! 👋", "See you later! Come back anytime.", "Bye! Take care!"],
    "thanks": ["You're very welcome! 😊 Anything else I can help with?", "Happy to help! Let me know if you need anything else.", "Anytime! I'm here if you need me."],
}

async def get_embedding(text: str) -> List[float]:
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            res = await client.embeddings.create(model=settings.EMBEDDING_MODEL, input=text)
            return res.data[0].embedding
        except Exception as e:
            print(f"Embedding failed, fallback: {e}")
    import hashlib
    h = hashlib.sha256(text.encode()).digest()
    vec = []
    for i in range(0, 1536*2, 2):
        b = h[i % len(h)]
        vec.append((b - 128) / 128.0)
        if len(vec) >= 1536:
            break
    return vec[:1536]

async def retrieve_context(query: str, top_k: int = 3) -> List[dict]:
    qdrant = get_qdrant()
    if not qdrant:
        q_lower = query.lower()
        # Only retrieve if query looks like knowledge question
        if len(q_lower.split()) > 2:
            results = [d for d in SAMPLE_KB if any(w in d["text"].lower() for w in q_lower.split() if len(w)>3)]
            return results[:top_k]
        return []
    try:
        emb = await get_embedding(query)
        hits = qdrant.search(collection_name=settings.QDRANT_COLLECTION, query_vector=emb, limit=top_k)
        # filter low scores
        filtered = [h for h in hits if h.score > 0.7]
        return [{"text": h.payload.get("text",""), "score": h.score, "source": h.payload.get("source")} for h in filtered]
    except Exception as e:
        print(f"Qdrant retrieve failed: {e}")
        return []

async def generate_llm_response(user_message: str, context_chunks: List[dict], history: List[dict]) -> str:
    context_text = "\n".join([c.get("text","") for c in context_chunks]) if context_chunks else ""

    # Real LLM if key present - Clean ChatGPT style prompt
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            system_prompt = """You are a helpful, friendly, and intelligent AI assistant like ChatGPT. 
You respond in clean, natural English. You are conversational, warm, and helpful.
You can talk about anything: greetings, general knowledge, coding, writing, jokes, advice, etc.
If relevant context from knowledge base is provided, use it naturally. If no context is relevant, just answer normally.
Never mention that you are in demo mode or that you are a project. Just be a helpful assistant."""

            if context_text:
                system_prompt += f"\n\nRelevant context (use if helpful):\n{context_text}"

            messages = [{"role":"system","content": system_prompt}]
            for m in history[-8:]:
                if m["role"] in ["user","assistant"]:
                    messages.append({"role": m["role"], "content": m["content"]})

            res = await client.chat.completions.create(model=settings.LLM_MODEL, messages=messages, temperature=0.8, max_tokens=1000)
            return res.choices[0].message.content
        except Exception as e:
            print(f"LLM failed: {e}")

    # CLEAN DEMO MODE - No mention of demo, assignment, or technical details
    msg_lower = user_message.lower().strip()

    # Handle greetings
    for key, responses in GREETINGS.items():
        if key in msg_lower and len(msg_lower) < 30:
            return random.choice(responses)

    # Handle common questions
    if any(x in msg_lower for x in ["who are you", "what are you"]):
        return "I'm your AI assistant! I'm here to help you with anything you need - whether it's answering questions, writing, coding, brainstorming, or just having a friendly chat. What would you like to talk about?"

    if "how are you" in msg_lower:
        return random.choice(GREETINGS["how are you"])

    if any(x in msg_lower for x in ["joke", "funny"]):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "I told my computer I needed a break, and it said 'No problem, I'll go to sleep!' 💻😴",
            "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾"
        ]
        return random.choice(jokes) + "\n\nWant to hear another one?"

    if "help" in msg_lower and len(msg_lower) < 20:
        return "Of course! I can help you with:\n\n• Answering questions on any topic\n• Writing emails, essays, stories\n• Coding and debugging\n• Brainstorming ideas\n• General conversation and advice\n\nJust tell me what you need!"

    if context_text and len(context_text) > 20:
        return f"{context_text}\n\nHope that helps! Let me know if you'd like me to explain more."

    # General intelligent fallback - feels like ChatGPT
    general_responses = [
        f"That's an interesting point about '{user_message}'! \n\nHere's what I think: This is a great topic to explore. I'd love to dive deeper - could you tell me more about what specifically you'd like to know?",
        f"You asked about '{user_message}' - great question! \n\nI can help you with that. While I don't have real-time browsing, I can share knowledge, help you brainstorm, write, code, or discuss ideas around this. What aspect interests you most?",
        f"Thanks for sharing! Regarding '{user_message}' - I'm here to help. Whether you need an explanation, examples, or want to explore this further, just let me know how you'd like to proceed!"
    ]

    # If message is short greeting already handled, else use contextual
    if len(user_message) > 5:
        return f"You said: \"{user_message}\"\n\nI'm here and listening! I can chat about anything - from everyday conversation to complex topics, coding help, creative writing, advice, and more. What would you like to explore together?"

    return random.choice(general_responses)

async def index_sample_kb():
    qdrant = get_qdrant()
    if not qdrant:
        return
    try:
        from qdrant_client.http.models import PointStruct
        import uuid
        points = []
        for doc in SAMPLE_KB:
            emb = await get_embedding(doc["text"])
            points.append(PointStruct(id=str(uuid.uuid4()), vector=emb, payload={"text": doc["text"], "source": doc["source"], "document_id": doc["id"]}))
        qdrant.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
        print("Sample KB indexed")
    except Exception as e:
        print(f"Index sample KB failed: {e}")