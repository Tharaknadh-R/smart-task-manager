from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TaskStatus
from app.models.task import Task
from app.models.user import User

async def update_user_status( db: AsyncSession, user_id: str, is_active: bool) -> User:
    result = await db.execute(
        select(User).where(User.user_id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_active = is_active

    if not is_active:
        task_result = await db.execute(
            select(Task).where(
                Task.assigned_to == user.id,
                Task.status == TaskStatus.IN_PROGRESS
            )
        )
        tasks = task_result.scalars().all()
        
        for task in tasks:
                task.status = TaskStatus.PENDING

    
    await db.commit()
    await db.refresh(user)

    return user