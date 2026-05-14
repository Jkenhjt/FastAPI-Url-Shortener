from sqlalchemy import String, Integer, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseUrl(DeclarativeBase):
    pass


class Url(BaseUrl):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_url: Mapped[str] = mapped_column(String())
    shortened_url: Mapped[str] = mapped_column(String())

    clicks: Mapped[int] = mapped_column(BigInteger())
    user_id: Mapped[int] = mapped_column(Integer())

    def __repr__(self) -> str:
        return f"Url(id={self.id}, original_url={self.original_url}, shortened_url={self.shortened_url}, clicks={self.clicks}, user_id={self.user_id})"
