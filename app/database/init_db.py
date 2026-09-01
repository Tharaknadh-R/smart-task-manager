from app.database.database import engine
from app.models.base import Base

import app.models

async def init_db():
    print(Base.metadata.tables.keys())
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

