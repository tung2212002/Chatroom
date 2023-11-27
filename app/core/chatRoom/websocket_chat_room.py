from fastapi import WebSocket
from sqlalchemy.orm import Session
from typing import List, Dict
from app.schema.schema_user import User
import json
from datetime import datetime
from fastapi.encoders import jsonable_encoder
import uuid

from app.core.chatRoom.service_chat_room import set_room_activity, add_member_to_chat_room, remove_member_from_chat_room, create_chat_room, get_all_chat_room, delete_chat_room
from app.schema.schema_chat_room import ChatRoomCreate, ChatRoom
from app.helper.enum import typeChatRoom, typeFunction
from app.core.message.service_message import create_message, get_all_message, get_message_by_chat_room_id, delete_message, update_message

async def send_personal_message( message: str, websocket: WebSocket):
        await websocket.send_text(message)

async def send_personal_json( payload: dict, type_action, websocket: WebSocket):
        payload_json = jsonable_encoder(payload)
        payload = {
            "type_function": typeFunction.CHAT_ROOM,
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
async def broadcast_json(payload: dict, type_action, connections, db: Session):
        try:
            if not connections:
                return
            payload_json = jsonable_encoder(payload)
            for connection in connections:
                payload = {
                    "type_function": typeFunction.CHAT_ROOM,
                    "type_action": type_action,
                    "payload": payload_json,
                }
                await connection.send_json(payload)
        except Exception as e:
            print(e)
    
async def handle_chat_room( websocket: WebSocket,connection_manager, type_action: str, data: dict, current_user, db: Session):
    if type_action == typeChatRoom.CREATE:
        user_id = current_user.id
        status, status_code, response = create_chat_room(data, user_id, db)
        connections = connection_manager.get_all_connection().values()
        await broadcast_json(response,typeChatRoom.CREATE,  connections, db=db)
    elif type_action == typeChatRoom.GET_ALL:
        status, status_code, response = get_all_chat_room( db=db)
        await send_personal_json(response,typeChatRoom.GET_ALL, connection_manager.get_connection(current_user.id))
    elif type_action == typeChatRoom.DELETE:
        chat_room_id = data["chat_room_id"]
        status, status_code, response = delete_chat_room(current_user, chat_room_id, db)
        if response['message'] == "successfully":
            response = jsonable_encoder({
                "chat_room_id": chat_room_id,
            })
            connections = connection_manager.get_all_connection().values()
            await broadcast_json(response,typeChatRoom.DELETE, connections, db=db)
    elif type_action == typeChatRoom.JOIN:
        chat_room_id = data["chat_room_id"]
        response = add_member_to_chat_room(chat_room_id, current_user.id, db)
        print(current_user.id)
        if response is not None:
            response = jsonable_encoder({
                "chat_room_id": chat_room_id,
                "user": User(**current_user.__dict__),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        if not connection_manager.get_room(chat_room_id):
            connection_manager.set_room(chat_room_id, websocket, db)
            connections = connection_manager.get_all_connection().values()
            await broadcast_json({"chat_room_id": chat_room_id}, typeChatRoom.ACTIVE, connections, db=db)
        else:
            connection_manager.set_room(chat_room_id, websocket, db)
            connections = connection_manager.get_room(chat_room_id)
            broadcast_connections = []
            for connection in connections:
                if connection != websocket:
                    broadcast_connections.append(connection)
                print('response', response)
            await broadcast_json(response,typeChatRoom.JOIN, broadcast_connections, db=db)
    elif type_action == typeChatRoom.LEAVE:
        chat_room_id = data["chat_room_id"]
        response = remove_member_from_chat_room(chat_room_id, current_user.id, db)
        print(current_user.id)
        if response is not None:
            response = jsonable_encoder({
                "chat_room_id": chat_room_id,
                "user": User(**current_user.__dict__)
            })
        if len(connection_manager.get_room(chat_room_id)) == 1:
            connection_manager.remove_websocket_room(chat_room_id, websocket, db)
            connections = connection_manager.get_all_connection().values()
            await broadcast_json({"chat_room_id": chat_room_id}, typeChatRoom.INACTIVE, connections, db=db)
        else:
            connection_manager.remove_websocket_room(chat_room_id, websocket, db)
            await broadcast_json(response,typeChatRoom.LEAVE, connection_manager.get_room(chat_room_id), db=db)
         
    
    
    
         