from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.id_generator import generate_business_id
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    user_id = await generate_business_id(
        db=db,
        entity="USER",
        prefix="USR",
    )

    user = User(
        user_id=user_id,
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )
    
    await db.refresh(user)

    return user

async def authenticate_user(db: AsyncSession, email:str, password: str) -> User:
    result = await db.execute(
        select(User).where(User.email == email)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User acoount is inactive",
        )
    
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return user