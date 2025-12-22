from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create Async Engine
# echo=True will log SQL queries (useful for debugging)
engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

async def init_db():
    """
    Creates tables if they don't exist.
    In production, use Alembic migrations instead of this.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """
    Dependency to provide a database session.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
