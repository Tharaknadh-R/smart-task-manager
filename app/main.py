from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.database.database import AsyncSessionLocal
from app.database.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Smart task manager API is Running"}

@app.get("/health")
async def health_check():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        return {
            "database":result.scalar()
        }