from sqlalchemy.orm import Session

from app.schema.schema_message import MessageCreate, Message
from app.model import Message


def get_all(db: Session):
    return db.query(Message).all()

def get_by_id(id: int, db: Session):
    return db.query(Message).filter(Message.id == id).first()

def get_by_user_id(user_id: int, db: Session):
    return db.query(Message).filter(Message.user_id == user_id).all()

def get_by_chat_room_id(chat_room_id: int, db: Session):
    return db.query(Message).filter(Message.chat_room_id == chat_room_id).all()

def create(message: MessageCreate, chat_room_id: int, user_id: int, db: Session):
    db_message = Message(**message.dict(), chat_room_id=chat_room_id, user_id=user_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def delete(id: int, db: Session):
    db_message = get_by_id(id, db)
    db.delete(db_message)
    db.commit()
    return db_message

