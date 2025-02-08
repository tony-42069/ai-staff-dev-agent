import os
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import AsyncGenerator
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Create data directory in container
DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR}/ai_staff_dev.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Enable connection health checks
)

# Use sessionmaker with class_=AsyncSession for SQLAlchemy 1.4
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=30),
    reraise=True
)
async def init_db() -> None:
    """Initialize database with retries."""
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with proper error handling."""
    async_session = async_session_maker()
    try:
        yield async_session
        await async_session.commit()
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        await async_session.rollback()
        raise
    finally:
        await async_session.close()
