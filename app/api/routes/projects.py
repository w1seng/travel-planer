from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: ProjectStatus | None = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    items, total = project_service.list_projects(db, page=page, limit=limit, status=status)
    return ProjectListResponse(total=total, page=page, limit=limit, items=items)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return project_service.get_project(db, project_id)


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db, data)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    return project_service.update_project(db, project_id, data)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    #Returns 409 
    project_service.delete_project(db, project_id)