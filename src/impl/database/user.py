from ormar import BigInteger, Boolean, Model, String

from .metadata import database, metadata


class User(Model):
    class Meta:
        database = database
        metadata = metadata
        tablename = "users"

    # pyright: reportGeneralTypeIssues=false
    id: int = BigInteger(primary_key=True, autoincrement=False)
    username: str = String(max_length=255, nullable=False, unique=True)
    banned: bool = Boolean(default=False)
