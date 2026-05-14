from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseUser(DeclarativeBase):
    pass


class User(BaseUser):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String())
    password: Mapped[str] = mapped_column(String())
    token: Mapped[str] = mapped_column(String())

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, password={self.password}, token={self.token})"
