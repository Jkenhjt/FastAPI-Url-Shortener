from pydantic import BaseModel


class User_m(BaseModel):
    username: str
    password: str
