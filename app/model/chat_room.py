from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, event
from sqlalchemy.orm import relationship, validates

from app.db.base import Base

class ChatRoom(Base):
    __tablename__ = "chat_room"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    description = Column(String(100), index=True, nullable=True)
    active = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    members = relationship("User", secondary="chat_room_member", overlaps="chat_rooms")
    messages = relationship("Message", back_populates="chat_room", cascade="all, delete")
    owner = relationship("User", back_populates="owned_chat_rooms")





