from pydantic import BaseModel
from enum import Enum


class TaskBody(BaseModel):
    description: str
    priority: int | None = None
    is_complete: bool = False


class UserBody(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class SortOrders(Enum):
    ASC = "asc"
    DESC = "desc"
