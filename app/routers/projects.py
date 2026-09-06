from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import create_project, get_projects, get_project, update_project, delete_project

router = APIRouter(prefix="/projects",tags=["Projects"])

@router.post("", response_model=ProjectResponse)
async def create_project_endpoint(project_data: ProjectCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_project(db=db,project_data=project_data,current_user=current_user)

@router.get("", response_model=list[ProjectResponse])
async def get_all_projects(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_projects(db=db,current_user=current_user)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_endpoint(project_id: str, current_user: User = Depends(get_current_user), db: AsyncSession =Depends(get_db)):
    return await get_project(db=db, project_id = project_id, current_user=current_user)

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project_endpoint(project_id: str, project_data: ProjectUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_project(db=db, project_id=project_id, project_data=project_data, current_user=current_user)

@router.delete("/{project_id}")
async def delete_project_endpoint(project_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_project(db=db, project_id=project_id, current_user=current_user)
    return {
        "message": "Project deleted successfully"
    }