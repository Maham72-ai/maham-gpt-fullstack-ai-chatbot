# Full-Stack AI Chatbot - Complete Project

React + Tailwind | FastAPI + Pydantic | MongoDB + Qdrant | RAG

## Features 
- Register/Login with JWT + bcrypt hashing
- New Chat, Multiple Chats, Persistent History in MongoDB
- Grouped Sidebar: Today, Yesterday, Previous 7 Days, Older (based on last_message_at)
- Rename / Delete with ownership check
- RAG: Qdrant retrieval + LLM (OpenAI optional, demo fallback works without key)
- Ownership enforcement - cannot access other user's chats by changing ID
- Pydantic validation, loading states, error handling, responsive design

## Folder Structure
```
/backend  -> FastAPI
  app/main.py
  app/routers/auth.py, conversations.py, chat.py
  app/schemas/
  app/services/auth_service.py, rag_service.py
  app/db/mongo.py, qdrant.py
  app/core/config.py
/frontend -> React + Vite + Tailwind
  src/pages/Login, Register, Chat
  src/components/Sidebar, ChatArea
  src/api/client.js
```

## Setup

### 1. MongoDB & Qdrant (Docker)
```bash
docker-compose up -d
```
Or run locally: mongod and qdrant

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env -> add your MONGODB_URL and optional OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```
API Docs: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
# Create .env file
echo VITE_API_URL=http://localhost:8000 > .env
npm run dev
```
App: http://localhost:5173

### 4. Environment Variables (.env.example included)
- MONGODB_URL
- QDRANT_URL
- JWT_SECRET_KEY
- OPENAI_API_KEY (optional - demo mode works without it)
- FRONTEND_ORIGIN

## Sample Knowledge Base
Backend includes sample KB in rag_service.py (FastAPI, MongoDB, Qdrant, React, Pydantic) and auto-indexes on startup if Qdrant is running.

To add your own docs: use qdrant client to upsert embeddings.

## API Contract
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/me
POST /api/conversations
GET /api/conversations
GET /api/conversations/{id}
PATCH /api/conversations/{id}
DELETE /api/conversations/{id}
POST /api/conversations/{id}/messages

## How RAG Works
1. User message embedding
2. Qdrant search top 3
3. Context + history -> LLM
4. If no context, response says cannot find supported answer

## Acceptance Criteria - All Done
- Register/Login/Logout ✓
- Protected endpoints ✓
- Multiple independent chats ✓
- Persistence after refresh ✓
- Date grouping ✓
- Rename/Delete owned only ✓
- ID tampering blocked ✓
- RAG retrieval ✓
- No secrets in frontend ✓

Enjoy!
