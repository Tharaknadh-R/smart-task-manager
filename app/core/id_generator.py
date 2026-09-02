from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.counter import IDCounter

async def generate_business_id(db: AsyncSession, entity: str, prefix: str) -> str:
    result = await db.execute(
        select(IDCounter)
        .where(IDCounter.entity == entity)
        .with_for_update()
    )

    counter = result.scalar_one_or_none()

    if counter is None:
        counter = IDCounter(entity=entity, value=1)
        db.add(counter)
    else:
        counter.value += 1

    await db.flush()
    return f"{prefix}{counter.value:03d}"