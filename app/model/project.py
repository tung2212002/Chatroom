from sqlalchemy import String, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    description = Column(String(100), index=True, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    
    collaborators = relationship("User", secondary="project_user", overlaps="projects")

