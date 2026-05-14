from typing import Annotated
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Cookie, Request
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import MultipleResultsFound, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from database.db import urls_db, users_db
from models.url import Url
from models.user import User
from schemas.admin import LinkAdd, LinkDelete, LinkGetData
from utils.utils import generate_url
from utils.limiter import limiter
from utils.logger import logger

load_dotenv()

DOMAIN = os.getenv("DOMAIN")


admin = APIRouter(prefix="/admin")


async def is_user_exist(request: Request, user_db: users_db) -> User | None:
    token: str = request.cookies.get("token")

    try:
        if token is None:
            logger.warning("User hasn't exist")
            raise HTTPException(status_code=403)

        result = (
            await user_db.execute(select(User).where(User.token == token))
        ).scalar_one_or_none()

        if result is None:
            logger.warning("User hasn't exist")
            raise HTTPException(status_code=403)

        return result

    except (IntegrityError, SQLAlchemyError) as e:
        logger.exception(f"DB Error: {e}!")

        raise HTTPException(status_code=500, detail="Server error!")


@admin.post(
    "/add",
    tags=["Admin"],
    responses={
        400: {
            "model": LinkAdd,
            "description": "Incorrect URL! Maybe already exist.",
        },
        403: {"description": "Incorrect token! Login first!"},
        500: {"description": "Server error!"},
    },
)
@limiter.limit("100/minute")
async def add_link(
    link: LinkAdd,
    urls_db: urls_db,
    request: Request,
    user: User | None = Depends(is_user_exist),
):
    try:
        s_url = f"http://{DOMAIN}/{generate_url()}"
        await urls_db.execute(
            insert(Url).values(
                original_url=link.link,
                shortened_url=s_url,
                clicks=0,
                user_id=user.id,
            )
        )
        await urls_db.commit()

    except MultipleResultsFound as e:
        logger.exception(f"sqlalchemy.exc.MultipleResultsFound: {e}!")

        await urls_db.rollback()
        raise HTTPException(status_code=400)

    except (IntegrityError, SQLAlchemyError) as e:
        logger.exception(f"DB Error: {e}!")

        await urls_db.rollback()
        raise HTTPException(status_code=500, detail="Server error!")

    return {"original_url": link.link, "shortened_url": s_url}


@admin.delete(
    "/delete",
    tags=["Admin"],
    responses={
        400: {
            "model": LinkDelete,
            "description": "Incorrect URL! Maybe isn't exist.",
        },
        403: {"description": "Incorrect token! Login first!"},
        500: {"description": "Server error!"},
    },
)
@limiter.limit("100/minute")
async def delete_link(
    shortened_link: LinkDelete,
    urls_db: urls_db,
    request: Request,
    user: User | None = Depends(is_user_exist),
):
    try:
        is_exist = (
            await urls_db.execute(
                select(Url).where(
                    Url.shortened_url == shortened_link.link,
                    Url.user_id == user.id,
                )
            )
        ).scalar_one_or_none()
        if is_exist is None:
            logger.warning(f"User in db is not exist {request.client.host}!")
            raise HTTPException(status_code=400)

        await urls_db.execute(
            delete(Url).where(
                Url.shortened_url == shortened_link.link,
                Url.user_id == user.id,
            )
        )
        await urls_db.commit()

    except (IntegrityError, SQLAlchemyError) as e:
        logger.exception(f"DB Error: {e}!")

        await urls_db.rollback()
        raise HTTPException(status_code=500, detail="Server error!")


@admin.get(
    "/get_all",
    tags=["Admin"],
    responses={
        400: {"description": "Incorrect URL! Maybe isn't exist."},
        403: {"description": "Incorrect token! Login first!"},
        500: {"description": "Server error!"},
    },
)
@limiter.limit("100/minute")
async def get_all_links(
    urls_db: urls_db,
    request: Request,
    user: User | None = Depends(is_user_exist),
):
    try:
        urls = (await urls_db.execute(select(Url).where(Url.user_id == user.id))).scalars()
        if urls is None:
            raise HTTPException(status_code=400)

        url_list = []
        for i in urls:
            url_list.append(
                {
                    "original_url": i.original_url,
                    "shortened_url": i.shortened_url,
                    "clicks": i.clicks,
                }
            )
        return url_list

    except (IntegrityError, SQLAlchemyError) as e:
        logger.exception(f"DB Error: {e}!")

        raise HTTPException(status_code=500, detail="Server error!")


@admin.post(
    "/get_link",
    tags=["Admin"],
    responses={
        400: {
            "model": LinkGetData,
            "description": "Incorrect URL! Maybe already exist.",
        },
        403: {"description": "Incorrect token! Login first!"},
        500: {"description": "Server error!"},
    },
)
@limiter.limit("100/minute")
async def get_link_data(
    shortened_link: LinkGetData,
    urls_db: urls_db,
    request: Request,
    user: User | None = Depends(is_user_exist),
):
    try:
        url = (
            await urls_db.execute(
                select(Url).where(
                    Url.shortened_url == shortened_link.link,
                    Url.user_id == user.id,
                )
            )
        ).scalar_one_or_none()
        if url is None:
            logger.warning(f"Url in db hasn't exist {request.client.host}!")
            raise HTTPException(status_code=400, detail="Url not found")

        return {
            "original_url": url.original_url,
            "shortened_url": url.shortened_url,
            "clicks": url.clicks,
        }

    except (IntegrityError, SQLAlchemyError) as e:
        logger.exception(f"DB Error: {e}!")

        raise HTTPException(status_code=500, detail="Server error!")
