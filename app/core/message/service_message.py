from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.base import get_db
from app.crud import messageCRUD, userCRUD
from app.helper.enum import constant
from app.schema.schema_message import MessageCreate, Message
from app.schema.schema_user import UserBase, User

def get_all_message(db: Session):
    db_messages = messageCRUD.get_all(db)
    if db_messages is None:
        return constant.ERROR, 404, {"message": "Message not found"}
    for db_message in db_messages:
        owner = userCRUD.get_by_id(db_message.user_id, db)
        if owner is None:
            return constant.ERROR, 404, {"message": "Owner not found"}
        response = db_message
        owner = User(**owner.__dict__)
        response.owner = owner
        # db_message = Message(**db_message.__dict__)
    return constant.SUCCESS, 200, db_messages

def get_message_by_id(id: int, db: Session):
    db_message = messageCRUD.get_by_id(id, db)
    if db_message is None:
        return constant.ERROR, 404, {"message": "Message not found"}
    owner = userCRUD.get_by_id(db_message.user_id, db)
    if owner is None:
        return constant.ERROR, 404, {"message": "Owner not found"}
    response = db_message
    owner = User(**owner.__dict__)
    response.owner = owner
    return constant.SUCCESS, 200, db_message


def get_message_by_user_id(user_id: int, db: Session):
    user = userCRUD.get_by_id(user_id, db)
    if user is None:
        return constant.ERROR, 404, {"message": "User not found"}
    db_messages = user.messages
    if db_messages is None:
        return constant.ERROR, 404, {"message": "Message not found"}
    response = db_messages
    return constant.SUCCESS, 200, response

def get_message_by_chat_room_id(chat_room_id: int, db: Session):
    db_messages = messageCRUD.get_by_chat_room_id(chat_room_id, db)
    if db_messages is None:
        return constant.ERROR, 404, {"message": "Message not found"}
    for db_message in db_messages:
        owner = userCRUD.get_by_id(db_message.user_id, db)
        if owner is None:
            return constant.ERROR, 404, {"message": "Owner not found"}
        response = db_message
        owner = User(**owner.__dict__)
        response.owner = owner
    response = db_messages
    return constant.SUCCESS, 200, response

def create_message(data: str, current_user, chat_room_id: int, db: Session):
    try:
        message = MessageCreate(content=data)
    except Exception as e:
        error = [f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()]
        return constant.ERROR, 400, error
    db_message = messageCRUD.create(message, chat_room_id, current_user.id, db)
    if db_message is None:
        return constant.ERROR, 404, {"message": "Chatroom not found"}
    owner = userCRUD.get_by_id(db_message.user_id, db)
    if owner is None:
        return constant.ERROR, 404, {"message": "Owner not found"}
    response = db_message
    owner = User(**owner.__dict__)
    response.owner = owner
    return constant.SUCCESS, 200, response

def update_message(current_user, id: int, data: str, db: Session):
    if current_user is None:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    db_message = messageCRUD.get_by_id(id, db)
    if db_message is None:
        return constant.ERROR, 404, {"message": "not found"}
    if db_message.user_id != current_user.id:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    try:
        message = MessageCreate(content=data)
    except Exception as e:
        error = [f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()]
        return constant.ERROR, 400, error
    db_message = messageCRUD.update(id, message, db)
    return constant.SUCCESS, 200, {"message": "successfully",
                                      "data": db_message}


def delete_message(current_user, id: int, db: Session):
    if current_user is None:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    db_message = messageCRUD.get_by_id(id, db)
    if db_message is None:
        return constant.ERROR, 404, {"message": "not found"}
    if db_message.user_id != current_user.id:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    db_message = messageCRUD.delete(id, db)
    return constant.SUCCESS, 200, {"message": "successfully",
                                      "data": db_message}   
                                   
