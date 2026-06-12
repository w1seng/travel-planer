from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.place import PlaceCreate, PlaceUpdate, PlaceResponse
from app.services import place_service

router = APIRouter(prefix="/projects/{project_id}/places", tags=["Places"])


@router.get("", response_model=list[PlaceResponse])
def list_places(project_id: int, db: Session = Depends(get_db)):
    return place_service.list_places(db, project_id)


@router.get("/{place_id}", response_model=PlaceResponse)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    return place_service.get_place(db, project_id, place_id)


@router.post("", response_model=PlaceResponse, status_code=201)
def add_place(project_id: int, data: PlaceCreate, db: Session = Depends(get_db)):
    return place_service.add_place(db, project_id, data)


@router.patch("/{place_id}", response_model=PlaceResponse)
def update_place(project_id: int, place_id: int, data: PlaceUpdate, db: Session = Depends(get_db)):
    return place_service.update_place(db, project_id, place_id, data)