from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from src.impl.database import database

from .routes import router

app = FastAPI()

app.include_router(router)


@app.on_event("startup")
async def startup() -> None:
    await database.connect()
