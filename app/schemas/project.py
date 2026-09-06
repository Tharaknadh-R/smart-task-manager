from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(
        default=None,
        max_length=1000,
    )

class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default= None,
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

class ProjectResponse(BaseModel):
    project_id:str
    name: str
    description: str | None
    owner_id: int