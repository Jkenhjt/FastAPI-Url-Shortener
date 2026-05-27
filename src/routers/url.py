import os
from typing import Annotated

from dotenv import load_dotenv

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select, update

from database.db import urls_db
from models.url import Url
from utils.limiter import limiter
from utils.logger import logger
from utils.db import transaction_process

load_dotenv()
DOMAIN = os.getenv("DOMAIN")


url = APIRouter()


async def increment_clicks_url(url: Url, urls_db: urls_db):
    await transaction_process(
        urls_db,
        update(Url).where(Url.shortened_url == url.shortened_url).values(clicks=url.clicks + 1),
    )


async def get_original_url(s_url: str, urls_db: urls_db) -> Url:
    original_url = (
        await transaction_process(
            urls_db, select(Url).where(Url.shortened_url == f"http://{DOMAIN}/{s_url}")
        )
    ).scalar_one_or_none()

    if original_url is None:
        logger.warning(f"DB response is None!")

        raise HTTPException(status_code=400, detail="Url not found")

    await increment_clicks_url(original_url, urls_db)

    return original_url


@url.get("/{s_url}", tags=["Link"])
@limiter.limit("100000/minute")
async def redirect(
    s_url: str,
    urls_db: urls_db,
    original_url: Annotated[Url, Depends(get_original_url)],
    request: Request,
    response: Response,
):
    response.status_code = 308
    response.headers["Location"] = original_url.original_url
