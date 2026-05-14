from pydantic import BaseModel


class Link(BaseModel):
    link: str


class LinkAdd(Link):
    pass


class LinkDelete(Link):
    pass


class LinkGetData(Link):
    pass
