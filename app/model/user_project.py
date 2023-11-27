from sqlalchemy import String, Integer, Column, ForeignKey
from sqlalchemy.orm import Session, relationship

from app.db.base import Base

class ProjectUser(Base):
    __tablename__ = "project_user"
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), primary_key=True)