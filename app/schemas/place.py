from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional



# Request schemas
class PlaceCreate(BaseModel):
    external_id: int = Field(..., gt=0)


class PlaceUpdate(BaseModel):
    notes: Optional[str] = Field(None, max_length=2000)
    visited: Optional[bool] = Field(None)



# Response schemas
class PlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    external_id: int
    title: str
    artist: Optional[str]
    image_url: Optional[str]    
    notes: Optional[str]
    visited: bool
    created_at: datetime
    updated_at: datetime