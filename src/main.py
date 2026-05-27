from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import uvicorn

from routers.url import url
from routers.user import user
from routers.admin import admin
from database.db import async_engine_users, async_engine_urls
from models.url import Url
from models.user import User
from utils.limiter import limiter
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with async_engine_urls.begin() as conn:
            await conn.run_sync(Url.metadata.create_all)

        async with async_engine_users.begin() as conn:
            await conn.run_sync(User.metadata.create_all)

    except (IntegrityError, OperationalError, SQLAlchemyError, Exception) as e:
        logger.critical(f"sqlalchemy.exc.IntegrityError: {e}")

    yield


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(url)
app.include_router(user)
app.include_router(admin)


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, workers=1, reload=True)
