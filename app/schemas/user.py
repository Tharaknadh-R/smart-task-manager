from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class userResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool