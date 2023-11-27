from sqlalchemy.orm import Session

from app.schema.schema_chat_room import ChatRoomCreate, ChatRoom
from app.model import ChatRoom
from app.model import User
from app.crud.userCRUD import get_by_id as get_user_by_id

def get_all(db: Session):
    return db.query(ChatRoom).all()


def get_by_id(id: int, db: Session):
    chatroom = db.query(ChatRoom).filter(ChatRoom.id == id).first()
    return chatroom


def get_by_user_id(user_id: int, db: Session):
    return db.query(ChatRoom).filter(ChatRoom.owner_id == user_id).all()

def add_member(chat_room_id: int, user_id: int, db: Session):
    db_chat_room = get_by_id(chat_room_id, db)
    user = get_user_by_id(user_id, db)
    db_chat_room.members.append(user)
    db.commit()
    db.refresh(db_chat_room)
    return db_chat_room

def remove_member(chat_room_id: int, user_id: int, db: Session):
    db_chat_room = get_by_id(chat_room_id, db)
    user = get_user_by_id(user_id, db)
    db_chat_room.members.remove(user)
    db.commit()
    db.refresh(db_chat_room)
    return db_chat_room

def set_room_activity(chat_room_id: int, active: bool, db: Session):
    db_chat_room = get_by_id(chat_room_id, db)
    db_chat_room.active = active
    db.commit()
    db.refresh(db_chat_room)
    return db_chat_room

def create(chat_room: ChatRoomCreate, user_id: int, db: Session):
    db_chat_room = ChatRoom(**chat_room.dict(), owner_id=user_id)
    db.add(db_chat_room)
    db.commit()
    db.refresh(db_chat_room)
    return db_chat_room

def delete(id: int, db: Session):
    db_chat_room = get_by_id(id, db)
    db.delete(db_chat_room)
    db.commit()
    return db_chat_room

