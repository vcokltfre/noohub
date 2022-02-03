from dataclasses import dataclass
from enum import IntFlag
from functools import wraps
from hmac import compare_digest
from json import loads
from os import environ
from typing import Awaitable, Callable, Literal

from aioredis import Redis, from_url
from fastapi import Response
from jose import jwt
from ormar import NoMatch
from pydantic import BaseModel

from src.impl.database import Key

_Response = Response | BaseModel | None
_Decorated = Callable[..., Awaitable[_Response]]


@dataclass
class _Key:
    username: str
    project: str
    key_id: int


class Authenticator:
    def __init__(self) -> None:
        self.redis: Redis = from_url(environ["REDIS_URI"])

    def generate_jwt(self, username: str, project: str, key_id: int) -> str:
        return jwt.encode(
            {
                "u": username,
                "p": project,
                "k": key_id,
            },
            environ["JWT_SECRET"],
            algorithm="HS256",
        )

    def decode_jwt(self, token: str) -> _Key:
        data = jwt.decode(token, environ["JWT_SECRET"], algorithms=["HS256"])
        return _Key(username=data["u"], project=data["p"], key_id=data["k"])

    def _authorized(self, token: str) -> Literal[False] | _Key:
        try:
            user = self.decode_jwt(token)
        except jwt.JWTError:
            return False
        except KeyError:
            return False

        return user

    def require(self) -> Callable[[_Decorated], _Decorated]:
        def decorate(func: _Decorated) -> _Decorated:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> _Response:
                request = kwargs["request"]

                token = request.headers.get("Authorization")
                if not token:
                    return Response(status_code=401)

                if compare_digest(token, environ["TOKEN"]):
                    request.state.username = "_"
                    request.state.project = "*"

                    return await func(*args, **kwargs)

                auth = self._authorized(token)

                if not auth:
                    return Response(status_code=403)

                key = await self.get_key(auth.key_id)

                if not key:
                    return Response(status_code=403)

                request.state.username = auth.username
                request.state.project = key.project

                return await func(*args, **kwargs)

            return wrapper

        return decorate

    async def get_key(self, key_id: int) -> Literal[False] | Key:
        cached = await self.redis.get(f"key:{key_id}")
        if cached:
            key = Key(**loads(cached))
        else:
            try:
                key = await Key.objects.first(id=key_id)
            except NoMatch:
                return False

        if not key.active:
            return False

        if not cached:
            await self.redis.set(f"key:{key_id}", key.json())

        return key
