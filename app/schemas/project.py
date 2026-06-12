from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional

from app.models.project import ProjectStatus
from app.schemas.place import PlaceCreate, PlaceResponse



# API accept
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = Field(None)

    places: list[PlaceCreate] = Field(
        default_factory=list,
        max_length=10,
        description="max 10 places",
    )


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None


# API return
class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  

    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    places: list[PlaceResponse] = []


class ProjectListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    page: int
    limit: int
    items: list[ProjectResponse]