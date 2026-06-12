import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.place import ProjectPlace
from app.models.project import Project, ProjectStatus
from app.schemas.place import PlaceCreate, PlaceUpdate
from app.services.aic_client import aic_client, AICClientError

logger = logging.getLogger(__name__)

MAX_PLACES_PER_PROJECT = 10



# Read
def get_place(db: Session, project_id: int, place_id: int) -> ProjectPlace:
    place = (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id, ProjectPlace.id == place_id)
        .first()
    )
    if not place:
        raise HTTPException(status_code=404, detail="Place not found in this project")
    return place


def list_places(db: Session, project_id: int) -> list[ProjectPlace]:
    return (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id)
        .order_by(ProjectPlace.created_at)
        .all()
    )



# Create
def add_place(db: Session, project_id: int, data: PlaceCreate) -> ProjectPlace:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    #max 10 places
    current_count = (
        db.query(ProjectPlace)
        .filter(ProjectPlace.project_id == project_id)
        .count()
    )
    if current_count >= MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=422,
            detail=f"Project already has the maximum of {MAX_PLACES_PER_PROJECT} places",
        )

    # no duplicates 
    duplicate = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.project_id == project_id,
            ProjectPlace.external_id == data.external_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail=f"Artwork {data.external_id} is already in this project",
        )

    try:
        artwork = aic_client.get_artwork(data.external_id)
    except AICClientError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    if artwork is None:
        raise HTTPException(
            status_code=404,
            detail=f"Artwork {data.external_id} not found in Art Institute of Chicago API",
        )

    place = ProjectPlace(
        project_id=project_id,
        external_id=artwork["external_id"],
        title=artwork["title"],
        artist=artwork["artist"],
        image_id=artwork["image_id"],
    )
    db.add(place)
    db.commit()
    db.refresh(place)

    logger.info(f"Added place external_id={data.external_id} to project {project_id}")
    return place



# Update
def update_place(db: Session, project_id: int, place_id: int, data: PlaceUpdate) -> ProjectPlace:
    place = get_place(db, project_id, place_id)

    if data.notes is not None:
        place.notes = data.notes

    if data.visited is not None:
        place.visited = data.visited

        if data.visited:
            _maybe_complete_project(db, place.project)

    db.commit()
    db.refresh(place)
    return place



def _maybe_complete_project(db: Session, project: Project) -> None:

    db.refresh(project)
    if project.is_completed:
        project.status = ProjectStatus.completed
        logger.info(f"Project {project.id} marked as completed")
        db.commit()