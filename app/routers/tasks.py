from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskStatusUpdate
from app.services.task_service import create_task, get_tasks, get_task, update_task, update_task_status, delete_task
from app.services.attachment_service import upload_attachment, get_task_attachments
from app.schemas.attachment import AttachmentResponse

router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["Tasks"],
)

@router.post("", response_model=TaskResponse)
async def task_create_endpoint( project_id: str, task_data: TaskCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_task(db=db, project_id=project_id, task_data=task_data, current_user=current_user)

@router.get("", response_model=list[TaskResponse])
async def get_tasks_endpoint(project_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_tasks(db=db, project_id=project_id, current_user=current_user)


task_router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)

@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(task_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_task(db=db, task_id=task_id, current_user=current_user)

@task_router.patch("/{task_id}", response_model=TaskResponse)
async def update_task_endpoint( task_id: str, task_data: TaskUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_task( db=db, task_id=task_id, task_data=task_data, current_user=current_user)

@task_router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status_endpoint(task_id: str, status_data: TaskStatusUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_task_status(db=db, task_id=task_id, new_status=status_data.status, current_user=current_user)

@task_router.delete("/{task_id}")
async def delete_task_endpoint( task_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_task( db=db, task_id=task_id, current_user=current_user)
    return {
        "message": "Task deleted successfully"
    }

@task_router.post("/{task_id}/attachments", response_model=AttachmentResponse)
async def upload_attachment_endpoint(task_id: str, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await upload_attachment(db=db, task_id=task_id, file=file, current_user=current_user)

@task_router.get("/{task_id}/attachments", response_model=list[AttachmentResponse])
async def get_task_attachments_endpoint(task_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_task_attachments(db=db, task_id=task_id, current_user=current_user)