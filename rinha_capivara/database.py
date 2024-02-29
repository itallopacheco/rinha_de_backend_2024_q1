from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from rinha_capivara.settings import Settings

async_engine = create_async_engine(Settings().DATABASE_URL, pool_size=5, max_overflow=10)
async_session_factory = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session():
    async with async_session_factory() as session:
        yield session
