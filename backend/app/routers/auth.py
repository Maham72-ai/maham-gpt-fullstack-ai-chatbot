from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime, timezone
from bson import ObjectId
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.services.auth_service import hash_password, authenticate_user, create_access_token, get_user_by_email, decode_token, get_user_by_id
from app.db.mongo import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

def user_to_response(user) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user["created_at"]
    )

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ",1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/register", response_model=UserResponse)
async def register(req: RegisterRequest):
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    existing = await get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db = get_db()
    now = datetime.now(timezone.utc)
    user_doc = {
        "name": req.name.strip(),
        "email": req.email.lower().strip(),
        "password_hash": hash_password(req.password),
        "created_at": now,
        "updated_at": now
    }
    result = await db["users"].insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_to_response(user_doc)

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    user = await authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token, user=user_to_response(user))

@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def me(current_user = Depends(get_current_user)):
    return user_to_response(current_user)
