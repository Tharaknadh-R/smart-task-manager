from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.core.security import create_access_token
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.user import UserCreate, userResponse, UserLogin
from app.services.auth_service import create_user, authenticate_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=userResponse)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user( db=db, user_data=user)

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    authenticated_user = await authenticate_user( db=db, email=user.email, password=user.password)

    access_token = create_access_token(user_id=authenticated_user.user_id)

    return{
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=userResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/admin-test")
async def admin_test( current_admin: User = Depends(get_current_admin)):
    return{
        "message": "Admin access granted",
        "user_id": current_admin.user_id,
        "name": current_admin.name,
        "role": current_admin.role.value,
    }