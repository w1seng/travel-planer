from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProjectPlace(Base):
    __tablename__ = "project_places"

    id          = Column(Integer, primary_key=True, index=True)
    project_id  = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Data from API
    external_id = Column(Integer, nullable=False)          
    title       = Column(String(500), nullable=False)      
    artist      = Column(String(500), nullable=True)        
    image_id    = Column(String(255), nullable=True)        

    # User data
    notes       = Column(String(2000), nullable=True)
    visited     = Column(Boolean, nullable=False, default=False, server_default="0")

    created_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Without dublicates of one place
    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="uq_project_external"),
    )

    # relatinships
    project = relationship("Project", back_populates="places")


    @property
    def image_url(self) -> str | None:
        if self.image_id:
            return f"https://www.artic.edu/iiif/2/{self.image_id}/full/400,/0/default.jpg"
        return None

    def __repr__(self) -> str:
        return f"<ProjectPlace id={self.id} external_id={self.external_id} visited={self.visited}>"