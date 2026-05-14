import sys
import os
from typing import Annotated

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.exc import (
    ArgumentError,
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)
from fastapi import Depends
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL_USERS = os.getenv("DATABASE_URL_USERS")
DATABASE_URL_URLS = os.getenv("DATABASE_URL_URLS")

try:
    async_engine_users = create_async_engine(DATABASE_URL_USERS, echo=True)
    async_engine_urls = create_async_engine(DATABASE_URL_URLS, echo=True)

    async_users = async_sessionmaker(
        async_engine_users, expire_on_commit=False, class_=AsyncSession
    )
    async_urls = async_sessionmaker(async_engine_urls, expire_on_commit=False, class_=AsyncSession)

    async def async_session_users():
        async with async_users() as session:
            yield session

    async def async_session_urls():
        async with async_urls() as session:
            yield session

except (ArgumentError, IntegrityError, OperationalError, SQLAlchemyError, Exception) as e:
    logger.critical(f"Exception: {e}")

    sys.exit(-1)


users_db = Annotated[AsyncSession, Depends(async_session_users)]
urls_db = Annotated[AsyncSession, Depends(async_session_urls)]
