from ormar import BigInteger, Boolean, Model, String

from .metadata import database, metadata


class Key(Model):
    class Meta:
        database = database
        metadata = metadata
        tablename = "keys"

    # pyright: reportGeneralTypeIssues=false
    id: int = BigInteger(primary_key=True, autoincrement=False)
    user: str = String(max_length=255)
    name: str = String(max_length=255)
    project: str = String(max_length=255, default="*")
    active: bool = Boolean(default=True)
