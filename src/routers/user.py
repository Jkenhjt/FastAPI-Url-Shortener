from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy import select, insert, update

from database.db import users_db
from schemas.user import User_m
from models.user import User
from security.security import create_token, hash_pass, compare_pass
from utils.limiter import limiter
from utils.logger import logger
from utils.db import transaction_process


user = APIRouter(prefix="/user")


async def is_user_exist(user_m: User_m, user_db: users_db) -> User | None:
    result = (
        await transaction_process(user_db, select(User).where(User.username == user_m.username))
    ).scalar_one_or_none()

    if result is None:
        logger.warning("User hasn't exist")

        return None

    return result


@user.post(
    "/register",
    tags=["User"],
    responses={
        400: {
            "model": User_m,
            "description": "Incorrect username or password!",
        },
        500: {"description": "Server error!"},
    },
)
@limiter.limit("5/hour")
async def register(
    user_m: User_m,
    user_db: users_db,
    request: Request,
    response: Response,
    user: Annotated[User | None, Depends(is_user_exist)],
):
    if user is not None:
        raise HTTPException(status_code=400)

    password = await hash_pass(user_m.password)

    await transaction_process(
        user_db, insert(User).values(username=user_m.username, password=password, token="")
    )

    result = (
        await transaction_process(user_db, select(User).where(User.username == user_m.username))
    ).scalar_one()

    token = await create_token(result.id)

    await transaction_process(
        user_db, update(User).where(User.username == user_m.username).values(token=token)
    )
    response.set_cookie(key="token", value=token)


@user.post(
    "/login",
    tags=["User"],
    responses={
        400: {
            "model": User_m,
            "description": "Incorrect username or password!",
        },
        500: {"description": "Server error!"},
    },
)
@limiter.limit("5/hour")
async def login(
    user_m: User_m,
    user_db: users_db,
    request: Request,
    response: Response,
    user: Annotated[User, Depends(is_user_exist)],
):
    result = await compare_pass(user_m.password, user.password)
    if result == False:
        logger.warning(f"Passwords are diffrent!")

        raise HTTPException(status_code=400)

    token = await create_token(user.id)

    await transaction_process(
        user_db,
        update(User)
        .where(User.username == user.username, User.password == user.password)
        .values(token=token),
    )

    response.set_cookie(key="token", value=user.token)
