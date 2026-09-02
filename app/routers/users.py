from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db

from app.core.dependencies import get_current_admin
from app.models.user import User
from app.schemas.user import userResponse
from app.schemas.user_status import UserStatusUpdate
from app.services.user_service import update_user_status

router = APIRouter(prefix="/users", tags=["Users"])

@router.patch("/{user_id}/status", response_model=userResponse)
async def change_user_status( 
    user_id: str, 
    status_data: UserStatusUpdate, 
    current_admin: User =Depends(get_current_admin), 
    db: AsyncSession = Depends(get_db),
):
    return await update_user_status(
        db=db,
        user_id=user_id,
        is_active=status_data.is_active,
    )