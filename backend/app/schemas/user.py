from typing import Optional
from datetime import datetime
from app.schemas.base import CamelModel

class UserBase(CamelModel):
    email: str
    name: str
    role: str = "admin"
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(CamelModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime

class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
