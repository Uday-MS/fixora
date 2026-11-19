from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=ApiResponse[TokenResponse])
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Public registration endpoint.
    Strictly assigns the normal 'user' role. Unconditionally ignores client-supplied roles.
    """
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

@router.get("/admin/status", response_model=ApiResponse[dict])
async def check_admin_status(current_admin: User = Depends(require_admin)):
    """Privileged administrative endpoint. Rejects normal users with HTTP 403 Forbidden."""
    return ApiResponse(
        data={
            "adminId": current_admin.id,
            "email": current_admin.email,
            "role": current_admin.role,
            "adminAccessGranted": True,
        },
        message="Administrator privilege verified.",
    )
