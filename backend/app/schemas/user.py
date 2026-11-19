from typing import Optional
from datetime import datetime
from pydantic import ConfigDict
from app.schemas.base import CamelModel

class UserRegister(CamelModel):
    """
    Public registration input schema.
    Strictly forbids role specification: ordinary public registrations
    are unconditionally assigned the 'user' role by the backend.
    """
    email: str
    name: str
    password: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

class UserCreate(CamelModel):
    """
    Internal / Administrative user creation schema.
    Used by administrative or bootstrapping processes.
    """
    email: str
    name: str
    password: str
    role: str = "user"
    avatar_url: Optional[str] = None

class UserBase(CamelModel):
    email: str
    name: str
    role: str = "user"
    avatar_url: Optional[str] = None

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
