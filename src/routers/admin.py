import os

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, insert, delete
from dotenv import load_dotenv

from database.db import urls_db, users_db
from models.url import Url
from models.user import User
from schemas.admin import LinkAdd, LinkDelete, LinkGetData
from utils.utils import generate_url
from utils.limiter import limiter
from utils.logger import logger
from utils.db import transaction_process

load_dotenv()

DOMAIN = os.getenv("DOMAIN")


admin = APIRouter(prefix="/admin")

responses_metadata = {
    403: {"description": "Incorrect token! Login first!"},
    500: {"description": "Server error!"},
}


async def is_user_exist(request: Request, user_db: users_db) -> User | None:
    token: str | None = request.cookies.get("token")

    if token is None:
        logger.warning("User hasn't exist, no token")
        raise HTTPException(status_code=403)

    result = (
        await transaction_process(user_db, select(User).where(User.token == token))
    ).scalar_one_or_none()

    if result is None:
        logger.warning("User hasn't exist, no in db")
        raise HTTPException(status_code=403)

    return result


@admin.post(
    "/add",
    tags=["Admin"],
    responses={
        400: {
            "model": LinkAdd,
            "description": "Incorrect URL! Maybe already exist.",
        },
    },
)
@limiter.limit("100/minute")
async def add_link(
    link: LinkAdd,
    urls_db: urls_db,
    request: Request,
    user: User = Depends(is_user_exist),
):
    s_url = f"http://{DOMAIN}/{generate_url()}"
    await transaction_process(
        urls_db,
        insert(Url).values(
            original_url=link.link,
            shortened_url=s_url,
            clicks=0,
            user_id=user.id,
        ),
    )
    return {"original_url": link.link, "shortened_url": s_url}


@admin.delete(
    "/delete",
    tags=["Admin"],
    responses={
        400: {
            "model": LinkDelete,
            "description": "Incorrect URL! Maybe isn't exist.",
        }
    },
)
@limiter.limit("100/minute")
async def delete_link(
    shortened_link: LinkDelete,
    urls_db: urls_db,
    request: Request,
    user: User = Depends(is_user_exist),
):
    is_exist = (
        await transaction_process(
            urls_db,
            select(Url).where(
                Url.shortened_url == shortened_link.link,
                Url.user_id == user.id,
            ),
        )
    ).scalar_one_or_none()
    if is_exist is None:
        logger.warning(f"User in db is not exist!")

        raise HTTPException(status_code=400)

    await transaction_process(
        urls_db,
        delete(Url).where(
            Url.shortened_url == shortened_link.link,
            Url.user_id == user.id,
        ),
    )


@admin.get(
    "/get_all",
    tags=["Admin"],
    responses={
        400: {"description": "Incorrect URL! Maybe isn't exist."},
    },
)
@limiter.limit("100/minute")
async def get_all_links(
    urls_db: urls_db,
    request: Request,
    user: User = Depends(is_user_exist),
):
    urls = (await transaction_process(urls_db, select(Url).where(Url.user_id == user.id))).scalars()
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


@admin.post(
    "/get_link",
    tags=["Admin"],
    responses={
        400: {
            "model": LinkGetData,
            "description": "Incorrect URL! Maybe already exist.",
        },
    },
)
@limiter.limit("100/minute")
async def get_link_data(
    shortened_link: LinkGetData,
    urls_db: urls_db,
    request: Request,
    user: User = Depends(is_user_exist),
):
    url = (
        await transaction_process(
            urls_db,
            select(Url).where(
                Url.shortened_url == shortened_link.link,
                Url.user_id == user.id,
            ),
        )
    ).scalar_one_or_none()
    if url is None:
        logger.warning(f"Url in db hasn't exist!")

        raise HTTPException(status_code=400, detail="Url not found")

    return {
        "original_url": url.original_url,
        "shortened_url": url.shortened_url,
        "clicks": url.clicks,
    }
