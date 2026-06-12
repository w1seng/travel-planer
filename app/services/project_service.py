import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.project import Project, ProjectStatus
from app.models.place import ProjectPlace
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.place_service import add_place
from app.schemas.place import PlaceCreate

logger = logging.getLogger(__name__)


# Read
def get_project(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def list_projects(
    db: Session,
    page: int = 1,
    limit: int = 10,
    status: ProjectStatus | None = None,
) -> tuple[list[Project], int]:
    query = db.query(Project)

    if status:
        query = query.filter(Project.status == status)

    total = query.count()
    items = (
        query
        .order_by(Project.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return items, total


# Create
def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    logger.info(f"Created project id={project.id} name={project.name!r}")

    for place_data in data.places:
        add_place(db, project_id=project.id, data=place_data)

    db.refresh(project)
    return project


# Update
def update_project(db: Session, project_id: int, data: ProjectUpdate) -> Project:
    project = get_project(db, project_id)

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.start_date is not None:
        project.start_date = data.start_date

    db.commit()
    db.refresh(project)
    return project



# Delete
def delete_project(db: Session, project_id: int) -> None:
    project = get_project(db, project_id)

    # cannot delete if any place is already visited
    has_visited = (
        db.query(ProjectPlace)
        .filter(
            ProjectPlace.project_id == project_id,
            ProjectPlace.visited == True,  
        )
        .first()
    )
    if has_visited:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a project that has visited places",
        )

    db.delete(project)
    db.commit()
    logger.info(f"Deleted project id={project_id}")