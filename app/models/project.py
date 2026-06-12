from sqlalchemy import Column, Integer, String, Date, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    active = "active"
    completed = "completed"

# project table
class Project(Base):
    __tablename__ = "projects"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    start_date  = Column(Date, nullable=True)
    status      = Column(
                    Enum(ProjectStatus),
                    nullable=False,
                    default=ProjectStatus.active,
                    server_default=ProjectStatus.active.value,
                  )
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


    # Relationships
    places = relationship(
        "ProjectPlace",
        back_populates="project",
        cascade="all, delete-orphan",  
        lazy="select",
    )


    @property
    def is_completed(self) -> bool:
        return bool(self.places) and all(p.visited for p in self.places)

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r} status={self.status}>"