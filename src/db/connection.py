"""
Database Connection Management

Handles async SQLite connection with WAL mode, proper pragmas,
and session lifecycle management.

Usage:
    from src.db.connection import get_db, init_db

    # Initialize (create tables)
    await init_db()

    # Use in FastAPI dependency injection
    async def my_endpoint(db: AsyncSession = Depends(get_db)):
        ...
"""

import sys
import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import event, text

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings
from src.db.models import Base


# Create async engine with SQLite optimizations
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False},  # Required for SQLite + async
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def configure_sqlite_pragmas(connection):
    """Apply SQLite performance and safety pragmas."""
    pragmas = [
        "PRAGMA journal_mode=WAL",          # Write-Ahead Logging for concurrency
        "PRAGMA busy_timeout=5000",          # Wait 5s on locks before failing
        "PRAGMA synchronous=NORMAL",         # Balance safety + speed
        "PRAGMA cache_size=-64000",          # 64MB page cache
        "PRAGMA foreign_keys=ON",            # Enforce foreign key constraints
        "PRAGMA temp_store=MEMORY",          # Temp tables in memory
        "PRAGMA mmap_size=268435456",        # 256MB memory-mapped I/O
    ]
    for pragma in pragmas:
        await connection.execute(text(pragma))


async def init_db():
    """Create all tables and apply pragmas."""
    async with engine.begin() as conn:
        await configure_sqlite_pragmas(conn)
        await conn.run_sync(Base.metadata.create_all)
    print("[DB] Database initialized successfully.")


async def drop_db():
    """Drop all tables (use with caution!)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("[DB] All tables dropped.")


async def get_db():
    """FastAPI dependency — yields an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_connection() -> dict:
    """Health check — verify database is accessible."""
    try:
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            return {"status": "healthy", "result": result.scalar()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# CLI support: python -m src.db.connection --init
if __name__ == "__main__":
    if "--init" in sys.argv:
        asyncio.run(init_db())
    elif "--check" in sys.argv:
        result = asyncio.run(check_connection())
        print(f"[DB] Health check: {result}")
    elif "--drop" in sys.argv:
        confirm = input("Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == "yes":
            asyncio.run(drop_db())
    else:
        print("Usage: python -m src.db.connection [--init|--check|--drop]")
