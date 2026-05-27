import os
import time

from authlib.jose import jwt
import bcrypt
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
assert SECRET_KEY is not None, "SECRET_KEY is not defioned in .env"


async def create_token(id: int) -> str:
    time_now = time.time_ns()
    header = {"alg": "HS256"}
    payload = {"sub": id, "iat": time_now, "expire": time_now + 1296000}

    return jwt.encode(header, payload, SECRET_KEY).decode()


async def decode_token(token: str) -> dict:
    result = jwt.decode(token, SECRET_KEY)
    result.validate()

    return result


async def hash_pass(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


async def compare_pass(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
