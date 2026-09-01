from fastapi import FastAPI
from sqlalchemy import text
from app.database.database import AsyncSessionLocal

app = FastAPI()

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