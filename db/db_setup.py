"""Database config file.

Yields:
    db: database connection
"""
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from configuration import configure

engine = create_engine(configure.dbConnectionUrl, future=True)

async_engine = create_async_engine(configure.dbAsyncConnectionUrl)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


Base = declarative_base()


# DB Utilities
def get_db() -> sessionmaker | Any:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def async_get_db() -> sessionmaker | Any:
    async with AsyncSessionLocal() as db:
        yield db
        await db.commit()
