from typing import AsyncGenerator
from app.config import DATABASE_URL

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

database_URL = DATABASE_URL
engine = create_async_engine(database_URL,  echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session