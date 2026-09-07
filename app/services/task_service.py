from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.id_generator import generate_business_id
from app.models.enums import TaskStatus, UserRole
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate

async def create_task(db: AsyncSession, project_id: str, task_data: TaskCreate, current_user: User) -> Task:
    result = await db.execute(
        select(Project).where(Project.project_id == project_id)
    )

    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if( current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "You do not have access to this project",
        )

    assigned_user = None

    if task_data.assigned_to is not None:
        assigned_result = await db.execute(
            select(User).where(
                User.user_id == task_data.assigned_to
            )
        )

        assigned_user = assigned_result.scalar_one_or_none()

    if task_data.assigned_to is not None and assigned_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    if not assigned_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot assign a task to an inactive user",
        )

    task_id = await generate_business_id(db=db, entity="TASK",prefix="TSK")

    task = Task(
        task_id = task_id,
        title = task_data.title,
        description=task_data.description,
        deadline=task_data.deadline,
        status=TaskStatus.PENDING,
        project_id=project.id,
        assigned_to = (
            assigned_user.id
            if assigned_user is not None
            else None
            ),
    )

    db.add(task)

    await db.commit()
    await db.refresh(task)

    return task

async def get_tasks(db: AsyncSession, project_id: str, current_user: User) -> list[Task]:
    result = await db.execute(
        select(Project).where(
            Project.project_id == project_id
        )
    )

    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if (current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        )

    task_result = await db.execute(
        select(Task).where(
            Task.project_id == project.id
        )
    )

    return list(task_result.scalars().all())

async def get_task(db: AsyncSession, task_id: str, current_user: User) -> Task:
    result = await db.execute(
        select(Task).where(Task.task_id== task_id)
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    project_result = await db.execute(
        select(Project).where(
            Project.id == task.project_id
        )
    )

    project = project_result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if( current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this task",
        )

    return task

async def update_task( db: AsyncSession, task_id: str, task_data: TaskUpdate, current_user: User) -> Task:
    result = await db.execute(
        select(Task).where(Task.task_id == task_id)
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    project_result = await db.execute(
        select(Project).where(Project.id == task.project_id)
    )

    project = project_result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if ( current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this task",
        )

    update_data = task_data.model_dump(exclude_unset=True)

    if "assigned_to" in update_data:
        assigned_user = None

        if update_data["assigned_to"] is not None:
            assigned_result = await db.execute(
                select(User).where(User.user_id == update_data["assigned_to"])
            )

        assigned_user = assigned_result.scalar_one_or_none()

        if assigned_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found",
            )

        if not assigned_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot assign a task to an inactive user",
            )

        update_data["assigned_to"] = assigned_user.id

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)

    return task

async def update_task_status(db: AsyncSession, task_id: str, new_status: TaskStatus, current_user: User) -> Task:
    result = await db.execute(
        select(Task).where(Task.task_id == task_id)
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    project_result = await db.execute(
        select(Project).where(
            Project.id == task.project_id
        )
    )

    project = project_result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if( current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this task",
        )

    valid_transitions = {
        TaskStatus.PENDING: {
            TaskStatus.IN_PROGRESS,
            TaskStatus.CANCELLED,
        },
        TaskStatus.IN_PROGRESS: {
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        },
        TaskStatus.COMPLETED: set(),
        TaskStatus.CANCELLED: set(),
    }

    if new_status not in valid_transitions[task.status]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Cannot change task status from "
                f"{task.status.value} to {new_status.value}"
            ),
        )

    task.status = new_status
    await db.commit()
    await db.refresh(task)

    return task

async def delete_task( db: AsyncSession, task_id: str, current_user: User) -> None:
    result = await db.execute(
        select(Task).where(Task.task_id == task_id)
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    project_result = await db.execute(
        select(Project).where(Project.id == task.project_id)
    )

    project = project_result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if ( current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this task",
        )

    await db.delete(task)
    await db.commit()