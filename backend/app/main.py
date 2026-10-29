from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.routers import auth, conversations, chat
from app.services.rag_service import index_sample_kb

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    try:
        await index_sample_kb()
    except Exception as e:
        print(f"KB index skip: {e}")
    yield
    await close_mongo_connection()

app = FastAPI(title="Full-Stack AI Chatbot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "API running", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}
