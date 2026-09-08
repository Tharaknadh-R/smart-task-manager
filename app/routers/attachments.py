from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.services.attachment_service import download_attachment, delete_attachment

router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"],
)

@router.get("/{attachment_id}/download")
async def download_attachment_endpoint(attachment_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> FileResponse:
    return await download_attachment(db=db, attachment_id=attachment_id, current_user=current_user)

@router.delete("/{attachment_id}")
async def delete_attachment_endpoint(attachment_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_attachment(db=db, attachment_id=attachment_id, current_user=current_user)
    return {
        "message": "Attachment deleted successfully"
    }