from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.base import get_db
from app.crud import chatRoomCRUD, userCRUD
from app.helper.enum import constant
from app.schema.schema_chat_room import ChatRoomCreate, ChatRoom
from app.schema.schema_user import  User


def get_all_chat_room( db: Session):
    db_chat_rooms = chatRoomCRUD.get_all(db)
    if db_chat_rooms is None:
        return constant.ERROR, 404, {"message": "Chatroom not found"}
    for db_chat_room in db_chat_rooms:
        owner = userCRUD.get_by_id(db_chat_room.owner_id, db)
        owner = User(**owner.__dict__)
        db_chat_room.user = owner

    return constant.SUCCESS, 200, db_chat_rooms

def get_chat_room_by_id(id: int, db: Session):
    db_chat_room = chatRoomCRUD.get_by_id(id, db)
    if db_chat_room is None:
        return constant.ERROR, 404, {"message": "Chatroom not found"}
    owner = userCRUD.get_by_id(db_chat_room.owner_id, db)
    if owner is None:
        return constant.ERROR, 404, {"message": "Owner not found"}
    response = db_chat_room
    owner = User(**owner.__dict__)
    response.owner = owner
    return constant.SUCCESS, 200, db_chat_room


def get_chat_room_by_user_id(user_id: int, db: Session):
    user = userCRUD.get_by_id(user_id, db)
    if user is None:
        return constant.ERROR, 404, {"message": "User not found"}
    db_chat_rooms = user.chat_rooms
    if db_chat_rooms is None:
        return constant.ERROR, 404, {"message": "Chatroom not found"}
    response = db_chat_rooms
    return constant.SUCCESS, 200, response

def get_chat_room_member_by_chat_room_id(chat_room_id: int, db: Session):
    db_chat_room = chatRoomCRUD.get_by_id(chat_room_id, db)
    if db_chat_room is None:
        return constant.ERROR, 404, {"message": "Chatroom not found"}
    db_chat_room_members = db_chat_room.members
    if db_chat_room_members is None:
        return constant.ERROR, 404, {"message": "Chatroom member not found"}
    response = db_chat_room_members
    return constant.SUCCESS, 200, response

def get_chat_room_message_by_chat_room_id(chat_room_id: int, db: Session):
    db_chat_room = chatRoomCRUD.get_by_id(chat_room_id, db)
    if db_chat_room is None:
        return constant.ERROR, 404, {"message": "Chatroom not found"}
    messages =  db_chat_room.messages
    if messages is None:
        return constant.ERROR, 404, {"message": "Chatroom message not found"}
    for message in messages:
        message.owner = User(**message.user.__dict__)
        message.user = None
    response = messages
    return constant.SUCCESS, 200, response

def create_chat_room(data: dict, user_id: int, db: Session):
    try:
        chat_room = ChatRoomCreate(**data)
    except Exception as e:
        error = [f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()]
        return constant.ERROR, 400, error
    db_chat_room = chatRoomCRUD.create(chat_room, user_id, db)
    user = userCRUD.get_by_id(user_id, db)
    if user is None:
        return constant.ERROR, 404, {"message": "User not found"}
    owner = User(**user.__dict__)
    db_chat_room_copy = ChatRoom(**db_chat_room.__dict__)
    db_chat_room_copy = {
        **db_chat_room_copy.__dict__,
        "user": owner   
    }
    response = db_chat_room_copy
    return constant.SUCCESS, 201, response


def delete_chat_room(current_user, id: int, db: Session):
    if current_user is None:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    db_chat_room = chatRoomCRUD.get_by_id(id, db)
    if db_chat_room is None:
        return constant.ERROR, 404, {"message": "Chatroom not found"}
    if db_chat_room.owner_id != current_user.id:
        return constant.ERROR, 401, {"message": "Unauthorized"}
    db_chat_room = chatRoomCRUD.delete(id, db)
    return constant.SUCCESS, 200, {"message": "successfully"}

def add_member_to_chat_room(chat_room_id: int, user_id: int, db: Session):
    try:
        db_user = userCRUD.get_by_id(user_id, db)
        if db_user is None:
            return constant.ERROR, 404, {"message": "User not found"}
        db_chat_room = chatRoomCRUD.add_member(chat_room_id, user_id, db)
        return True
    except Exception as e:
        print(e)
        return None    
def remove_member_from_chat_room( chat_room_id: int, user_id: int, db: Session):
    try:
        db_user = userCRUD.get_by_id(user_id, db)
        db_chat_room = chatRoomCRUD.remove_member(chat_room_id, user_id, db)
        return True
    except Exception as e:
        return None

def set_room_activity(chat_room_id: int, active: bool, db: Session):
    try:
        db_chat_room = chatRoomCRUD.set_room_activity(chat_room_id, active, db)
        return True
    except Exception as e:
        return None