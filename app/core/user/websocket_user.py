from fastapi import WebSocket
from sqlalchemy.orm import Session
from typing import List
from app.schema.schema_user import User
import json
from typing import Dict
from datetime import datetime
from fastapi.encoders import jsonable_encoder

from app.core.chatRoom.service_chat_room import set_room_activity, add_member_to_chat_room, remove_member_from_chat_room
from app.schema.schema_message import MessageCreate, Message
from app.schema.schema_user import UserBase, User
from app.helper.enum import typeUser, typeFunction
from app.core.user.service_user import set_user_active, get_user_by_id

async def send_personal_json(type_function, type_action,payload: dict, websocket: WebSocket):
        payload_json = jsonable_encoder(payload)
        payload = {
            "type_function": type_function,
            "type_action": type_action,
            "payload": payload_json,
        }
        await websocket.send_json(payload)

            
async def broadcast_json(type_function, type_action, data: dict, connections: Dict[int, WebSocket], db: Session):
        try:
            if not connections:
                return
            if type_action == typeUser.ONLINE:
                set_user_active(data["user"].id, True, db)
            elif type_action == typeUser.OFFLINE:
                set_user_active(data["user"].id, False, db)
            
            status, status_code, repsonse = get_user_by_id(data["user"].id, db)
            user = User(**repsonse.dict())
            user = jsonable_encoder(user)

            payload = {
                    "type_function": type_function,
                    "type_action": type_action,
                    "payload": {
                        "user": user
                    }
                }
            
            for connection in connections.values():
                await connection.send_json(payload)
        except Exception as e:
            print(e)
    
async def handle_user(connection_manager, type_action: str, data: dict, current_user, db: Session):
            if type_action == typeUser.ONLINE:
                await broadcast_json(typeFunction.USER, typeUser.ONLINE, data, connection_manager.get_all_connection(), db=db)
            elif type_action == typeUser.OFFLINE:
                await broadcast_json(typeFunction.USER, typeUser.OFFLINE, data, connection_manager.get_all_connection(), db=db)
            elif type_action == typeUser.ALL:
                user_online = []
                for id in connection_manager.get_all_connection().keys():
                    status, status_code, response = get_user_by_id(id, db)
                    user = User(**response.dict())
                    user_online.append(user)
                data = {
                    "users": user_online
                }
                await send_personal_json(typeFunction.USER, typeUser.ALL, data, connection_manager.get_connection(current_user.id))
