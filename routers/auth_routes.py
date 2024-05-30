from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.auth_service import (generate_nonce, pbkdf2_sha256, generate_token, authenticate, generate_dev_key,
                                   users, active_tokens, dev_keys)

router = APIRouter()


class UserCredentials(BaseModel):
    username: str
    password: str


class DevKeyResponse(BaseModel):
    dev_key: str


@router.post("/register")
async def register_route(credentials: UserCredentials):
    username = credentials.username
    password = credentials.password

    if username in users:
        raise HTTPException(status_code=400, detail="User already exists.")

    salt = generate_nonce(16)
    hashed_password = pbkdf2_sha256(password, salt, 4096, 32)

    users[username] = {"salt": salt, "hashed_password": hashed_password}
    return {"message": f"User {username} registered successfully."}


@router.post("/login")
async def login_route(credentials: UserCredentials):
    username = credentials.username
    password = credentials.password

    user = users.get(username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password.")

    salt = user["salt"]
    hashed_password = pbkdf2_sha256(password, salt, 4096, 32)

    if hashed_password != user["hashed_password"]:
        raise HTTPException(status_code=400, detail="Invalid username or password.")

    token = generate_token()
    active_tokens[token] = username
    return {"token": token}


@router.post("/create_dev_key")
async def create_dev_key_route(request: Request):
    token = request.headers.get("Authorization")

    if not authenticate(token):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing token.")

    username = active_tokens[token]
    dev_key = generate_dev_key()
    dev_keys[dev_key] = username

    return DevKeyResponse(dev_key=dev_key)
