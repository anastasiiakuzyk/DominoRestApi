import hashlib
import os
import base64
from typing import Dict
from pydantic import BaseModel
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

users: Dict[str, "User"] = {}
active_tokens: Dict[str, str] = {}
dev_keys: Dict[str, str] = {}


class User(BaseModel):
    salt: str
    hashed_password: str


security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return active_tokens[token]


def generate_nonce(length: int) -> str:
    return base64.b64encode(os.urandom(length)).decode('utf-8')


def pbkdf2_sha256(password: str, salt: str, iterations: int, key_len: int) -> str:
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations, dklen=key_len)
    return base64.b64encode(key).decode('utf-8')


def generate_token() -> str:
    return generate_nonce(32)


def generate_dev_key() -> str:
    return generate_nonce(32)


def authenticate(token: str) -> bool:
    return token in active_tokens


def verify_dev_key(dev_key: str) -> bool:
    return dev_key in dev_keys
