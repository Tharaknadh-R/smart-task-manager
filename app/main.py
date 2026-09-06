from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.database.database import AsyncSessionLocal
from app.database.init_db import init_db
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.projects import router as projects_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)

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