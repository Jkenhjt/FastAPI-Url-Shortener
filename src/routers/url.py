import logging
import os

from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.db import urls_db
from models.url import Url
from utils.limiter import limiter
from utils.logger import logger

load_dotenv()
DOMAIN = os.getenv("DOMAIN")


url = APIRouter()


@url.get("/{s_url}", tags=["Link"])
@limiter.limit("100000/minute")
async def redirect(s_url: str, urls_db: urls_db, request: Request, response: Response):
    try:
        original_url = (
            await urls_db.execute(
                select(Url).where(Url.shortened_url == f"http://{DOMAIN}/{s_url}")
            )
        ).scalar_one_or_none()

        if original_url is None:
            logger.warning(f"DB response is None {request.client.host}!")

            raise HTTPException(status_code=400, detail="Url not found")

        await urls_db.execute(
            update(Url)
            .where(Url.shortened_url == original_url.shortened_url)
            .values(clicks=original_url.clicks + 1)
        )
        await urls_db.commit()

    except (IntegrityError, SQLAlchemyError) as e:
        logger.exception(f"sqlalchemy.exc.IntegrityError: {e}!")

        raise HTTPException(status_code=500, detail="Server error!")

    response.status_code = 308
    response.headers["Location"] = original_url.original_url
