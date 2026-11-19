from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.models.workspace import Workspace
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse

class AuthService:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def register(db: AsyncSession, user_in: UserRegister) -> TokenResponse:
        email = user_in.email.strip().lower()
        existing = await AuthService.get_by_email(db, email)
        if existing:
            raise ValueError("A user with this email already exists.")

        # Security Policy:
        # Public registrations are ALWAYS assigned role="user".
        # Administrator accounts can ONLY be created through the secure environment bootstrap process.
        # Frontend/client role input is ignored and cannot escalate privileges.
        user = User(
            email=email,
            name=user_in.name.strip(),
            hashed_password=get_password_hash(user_in.password),
            role="user",
            avatar_url=user_in.avatar_url,
        )
        db.add(user)
        await db.flush()

        # Create default organization & workspace for the user
        org = Organization(
            name=f"{user.name}'s Org",
            slug=f"{user.email.split('@')[0]}-org",
        )
        db.add(org)
        await db.flush()

        member = OrganizationMember(
            organization_id=org.id,
            user_id=user.id,
            role="owner",
        )
        db.add(member)

        workspace = Workspace(
            organization_id=org.id,
            name=f"{user.name}'s Workspace",
            slug=f"{user.email.split('@')[0].lower().replace('.', '-')}-ws",
            plan="enterprise",
            member_count=1,
        )
        db.add(workspace)
        await db.commit()
        await db.refresh(user)

        access_token = create_access_token(user.id)
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    async def login(db: AsyncSession, login_in: UserLogin) -> TokenResponse:
        user = await AuthService.get_by_email(db, login_in.email)
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise ValueError("Invalid email or password.")
        if not user.is_active:
            raise ValueError("User account is inactive.")

        access_token = create_access_token(user.id)
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )
