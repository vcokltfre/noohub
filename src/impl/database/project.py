from ormar import JSON, BigInteger, Model, String

from .metadata import database, metadata


class Project(Model):
    class Meta:
        database = database
        metadata = metadata
        tablename = "projects"

    # pyright: reportGeneralTypeIssues=false
    id: int = BigInteger(primary_key=True)
    user: str = String(max_length=255)
    name: str = String(max_length=255)
    version: str = String(max_length=255)
    spec: dict = JSON()
