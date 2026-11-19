import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

logger = logging.getLogger("fixora.db")

Base = declarative_base()

def get_engine_url(url: str) -> str:
    # Ensure async driver is specified
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite:///") and not url.startswith("sqlite+aiosqlite:///"):
        url = url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    
    # asyncpg expects ssl=require rather than sslmode=require
    if "sslmode=require" in url:
        url = url.replace("sslmode=require", "ssl=require")
        
    return url

db_url = get_engine_url(settings.DATABASE_URL)
engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    pool_pre_ping=True if "sqlite" not in db_url else False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    # Import all models to register with Base.metadata
    from app.models import (
        user,
        organization,
        workspace,
        project,
        repository,
        bug,
        patch,
        test_run,
        incident,
        investigation,
        knowledge,
        integration,
        audit_log,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")
