from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import FileResponse

from app.core.id_generator import generate_business_id
from app.models.attachment import Attachment
from app.models.project import Project
from app.models.task import Task
from app.models.enums import UserRole
from app.models.user import User

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".png",
    ".jpg",
    ".jpeg",
}

MAX_FILE_SIZE = 10 * 1024 * 1024

async def upload_attachment(db: AsyncSession, task_id: str, file: UploadFile, current_user: User) -> Attachment:
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

    if( current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this task",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type is not allowed",
        )

    attachment_id = await generate_business_id(db=db, entity="ATTACHMENT", prefix="ATT")

    task_directory = Path("uploads") / task.task_id
    task_directory.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(file.filename).name

    file_path = task_directory / f"{attachment_id}_{safe_filename}"

    total_size = 0

    try:
        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    buffer.close()
                    file_path.unlink(missing_ok=True)

                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File size exceeds the 10MB limit",
                    )
                buffer.write(chunk)
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise

    attachment = Attachment(
        attachment_id=attachment_id,
        filename=file.filename,
        path=str(file_path),
        task_id=task.id,
    )

    db.add(attachment)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        file_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    await db.refresh(attachment)
    return attachment

async def get_task_attachments(db: AsyncSession, task_id: str, current_user: User) -> list[Attachment]:
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

    if(current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this task",
        )

    attachment_result = await db.execute(
        select(Attachment)
        .where(Attachment.task_id == task.id)
        .order_by(Attachment.created_at)
    )

    return attachment_result.scalars().all()

async def download_attachment(db: AsyncSession, attachment_id: str, current_user: User) -> FileResponse:
    result = await db.execute(
        select(Attachment).where(Attachment.attachment_id == attachment_id)
    )

    attachment = result.scalar_one_or_none()

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    task_result = await db.execute(
        select(Task).where(Task.id == attachment.task_id)
    )

    task = task_result.scalar_one_or_none()

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

    if( current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this attachment",
        )

    file_path = Path(attachment.path)

    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment file not found",
        )

    return FileResponse(
        path=file_path,
        filename=attachment.filename,
    )

async def delete_attachment(db: AsyncSession, attachment_id: str, current_user: User) -> None:
    result = await db.execute(
        select(Attachment).where(Attachment.attachment_id == attachment_id)
    )

    attachment = result.scalar_one_or_none()

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    task_result = await db.execute(
        select(Task).where(Task.id == attachment.task_id)
    )

    task = task_result.scalar_one_or_none()

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
            detail="Project not found"
        )

    if ( current_user.role != UserRole.ADMIN and project.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this attachment",
        )

    file_path = Path(attachment.path)

    if file_path.is_file():
        file_path.unlink()

    await db.delete(attachment)

    await db.commit()