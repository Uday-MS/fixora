from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=ApiResponse[TokenResponse])
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        token_resp = await AuthService.register(db, user_in)
        return ApiResponse(data=token_resp, message="Registration successful.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(login_in: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        token_resp = await AuthService.login(db, login_in)
        return ApiResponse(data=token_resp, message="Login successful.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=UserResponse.model_validate(current_user))
