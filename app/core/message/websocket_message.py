from fastapi import WebSocket
from sqlalchemy.orm import Session
from typing import List, Dict
from app.schema.schema_user import User
import json
from datetime import datetime
from fastapi.encoders import jsonable_encoder

from app.core.chatRoom.service_chat_room import set_room_activity, add_member_to_chat_room, remove_member_from_chat_room
from app.schema.schema_message import MessageCreate, Message
from app.helper.enum import typeChatRoom, typeMessage, typeFunction
from app.core.message.service_message import create_message, get_message_by_chat_room_id, delete_message, update_message

async def send_personal_message( message: str, websocket: WebSocket):
        await websocket.send_text(message)

async def send_personal_json( payload: dict, type_action, websocket: WebSocket):
        payload_json = jsonable_encoder(payload)
        payload = {
            "type_function": typeFunction.MESSAGE,
            "type_action": type_action,
            "payload": payload_json,
        }
        await websocket.send_json(payload)

async def broadcast( message: str, type_action, connections, db: Session):
        try:
            if not connections:
                return
            for connection in connections:
                await connection.send_text(message)
        except Exception as e:
            print(e)
async def broadcast_json( payload: dict, type_action, connections, db: Session):
        try:
            if not connections:
                return
            payload_json = jsonable_encoder(payload)
            for connection in connections:
                payload = {
                    "type_function": typeFunction.MESSAGE,
                    "type_action": type_action,
                    "payload": payload_json,
                }
                await connection.send_json(payload)
        except Exception as e:
            print(e)
    
async def handle_message( websocket: WebSocket,connection_manager, type_action: str, data: dict, current_user, db: Session):
    if type_action == typeMessage.CREATE:
        chat_room_id = data["chat_room_id"]
        status, status_code, response = create_message(data["content"], current_user, chat_room_id, db)
        response = {
                "chat_room_id": chat_room_id,
                "message": response,
            }
        await broadcast_json(response,typeMessage.CREATE, connection_manager.get_room(chat_room_id), db=db)
    elif type_action == typeMessage.GET_ALL:
        chat_room_id = data["chat_room_id"]
        status, status_code, response = get_message_by_chat_room_id(chat_room_id, db)
        response = {
                "chat_room_id": chat_room_id,
                "messages": response,
            }
        await send_personal_json(response,typeMessage.GET_ALL, websocket)
    elif type_action == typeMessage.DELETE:
        id = data["id"]
        chat_room_id = data["chat_room_id"]
        status, status_code, response = delete_message(current_user, id, db)
        response = {
                "chat_room_id": chat_room_id,
                "message": response,
            }
        await broadcast_json(response,typeMessage.DELETE, connection_manager.get_room(chat_room_id), db=db)
    elif type_action == typeMessage.UPDATE:
        id = data["id"]
        chat_room_id = data["chat_room_id"]
        content = data["content"]
        status, status_code, response = update_message(current_user, id, content, db)
        response = {
                "chat_room_id": chat_room_id,
                "message": response,
            }
        await broadcast_json(response,typeMessage.UPDATE, connection_manager.get_room(chat_room_id), db=db)
         