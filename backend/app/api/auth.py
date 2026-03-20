from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.db.mongodb import users_col

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest):
    col = users_col()

    # Check duplicate
    if await col.find_one({"email": body.email}):
        raise HTTPException(status_code=409, detail="Email already registered")

    user_doc = {
        "email": body.email,
        "name": body.name or body.email.split("@")[0],
        "password_hash": hash_password(body.password),
        "created_at": datetime.utcnow(),
        "streak_days": 0,
        "total_analyses": 0,
    }
    result = await col.insert_one(user_doc)
    user_id = str(result.inserted_id)

    token = create_access_token(user_id, body.email)
    return TokenResponse(
        access_token=token,
        user={"id": user_id, "email": body.email, "name": user_doc["name"]},
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    col = users_col()
    user = await col.find_one({"email": body.email})

    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token = create_access_token(user_id, body.email)
    return TokenResponse(
        access_token=token,
        user={"id": user_id, "email": body.email, "name": user.get("name", "")},
    )


@router.get("/me")
async def get_me(current_user: dict = None):
    # Dependency injection wired in routes that need auth
    return current_user
