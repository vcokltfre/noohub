from pydantic import BaseModel

from src.impl.database import Key
from src.impl.utils import Noofile


class UserRequest(BaseModel):
    username: str
    id: int


class KeyRequest(BaseModel):
    name: str
    project: str = "*"


class KeyResponse(BaseModel):
    key: Key
    token: str


class KeysResponse(BaseModel):
    keys: list[Key]


class ProjectResponse(BaseModel):
    name: str
    username: str
    spec: Noofile
    version: str
