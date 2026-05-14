from typing import Annotated
import logging

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.db import users_db
from schemas.user import User_m
from models.user import User
from security.security import create_token, hash_pass, compare_pass
from utils.limiter import limiter
from utils.logger import logger


user = APIRouter(prefix="/user")


async def is_user_exist(user_m: User_m, user_db: users_db) -> User | None:
    try:
        if user_m is None:
            logger.warning("User hasn't exist")
            raise HTTPException(status_code=400)

        result = (
            await user_db.execute(select(User).where(User.username == user_m.username))
        ).scalar_one_or_none()

        if result is None:
            logger.warning("User hasn't exist")
            return None

        return result

    except (IntegrityError, SQLAlchemyError) as e:
        logger.exception(f"DB Error: {e}!")

        raise HTTPException(status_code=500, detail="Server error!")


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
        logger.warning("User already exist")
        raise HTTPException(status_code=400)

    try:
        password = await hash_pass(user_m.password)

        await user_db.execute(
            insert(User).values(username=user_m.username, password=password, token="")
        )
        await user_db.commit()

        result = (
            await user_db.execute(select(User).where(User.username == user_m.username))
        ).scalar_one_or_none()
        await user_db.commit()

        token = await create_token(result.id)

        await user_db.execute(
            update(User).where(User.username == user_m.username).values(token=token)
        )
        await user_db.commit()

    except (IntegrityError, SQLAlchemyError) as e:
        logger.exception(f"DB Error: {e}!")

        await user_db.rollback()
        raise HTTPException(status_code=500)

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
    user: Annotated[User | None, Depends(is_user_exist)],
):
    result = await compare_pass(user_m.password, user.password)
    if result == False:
        logger.warning(f"Passwords {request.client.host} are diffrent!")

        raise HTTPException(status_code=400)

    token = await create_token(user.id)

    await user_db.execute(
        update(User)
        .where(User.username == user.username, User.password == user.password)
        .values(token=token)
    )
    await user_db.commit()

    response.set_cookie(key="token", value=user.token)
