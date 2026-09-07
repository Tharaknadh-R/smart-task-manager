from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import TaskStatus

class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    deadline: datetime | None = None
    assigned_to: str | None = None

class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: str | None
    deadline: str | None
    status: TaskStatus
    project_id: int
    assigned_to: int | None

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    deadline: datetime | None = None
    assigned_to: str | None = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    