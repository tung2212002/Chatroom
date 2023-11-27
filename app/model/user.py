from sqlalchemy import Boolean, String, Integer, Column
from sqlalchemy.orm import relationship

from app.db.base import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    hashed_password = Column(String(200))
    is_active = Column(Boolean, default=False)
    picture_path = Column(String(100), default="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/2048px-Default_pfp.svg.png")

    projects = relationship("Project", secondary="project_user",overlaps="collaborators")
    messages = relationship("Message", back_populates="user")
    chat_rooms = relationship("ChatRoom", secondary="chat_room_member", overlaps="members")
    owned_chat_rooms = relationship("ChatRoom", back_populates="owner")

    
  