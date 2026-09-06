from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.id_generator import generate_business_id
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.enums import UserRole, TaskStatus
from app.models.task import Task

async def create_project(db: AsyncSession, project_data: ProjectCreate, current_user: User) -> Project:
    project_id = await generate_business_id(db=db, entity="PROJECT", prefix="PRJ")

    project = Project(
        project_id= project_id,
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
    )

    db.add(project)

    await db.commit()
    await db.refresh(project)

    return project

async def get_projects(db: AsyncSession, current_user: User) -> list[Project]:
    if current_user.role == UserRole.ADMIN:
        result = await db.execute(select(Project))
    else:
        result = await db.execute(
            select(Project).where(
                Project.owner_id == current_user.id
            )
        )

    return list(result.scalars().all())

async def get_project(db: AsyncSession,project_id: str, current_user: User) -> Project:
    result = await db.execute(select(Project).where(Project.project_id == project_id))

    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if(current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        )

    return project

async def update_project(db: AsyncSession, project_id: str, project_data: ProjectUpdate, current_user: User) -> Project:
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

    if( current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        )

    update_data = project_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(project,field, value)

    await db.commit()
    await db.refresh(project)

    return project

async def delete_project(db: AsyncSession, project_id: str, current_user: User) -> None:
    result = await db.execute(
        select(Project).where(Project.project_id == project_id)
    )

    project = result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if(current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        )

    task_result = await db.execute(
        select(Task).where(
            Task.project_id == project_id,
        )
    )

    tasks = task_result.scalars.all()

    for task in tasks:
        if task.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Project cannot be deleted because it "
                    "has pending or in-progress tasks "
                ),
            )

    for task in tasks:
        await db.delete(task)

    await db.delete(project)
    await db.commit()