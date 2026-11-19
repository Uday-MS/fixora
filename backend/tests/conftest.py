import os
import pytest_asyncio

# Ensure tests run against an isolated test database, preserving fixora.db
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_fixora.db"

from app.db.session import init_db
from app.main import seed_initial_data

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    await init_db()
    await seed_initial_data()
