from fastapi import WebSocket
from sqlalchemy.orm import Session
from typing import List
import json
from typing import Dict
from datetime import datetime
from fastapi.encoders import jsonable_encoder

from app.core.chatRoom.service_chat_room import set_room_activity, add_member_to_chat_room, remove_member_from_chat_room
from app.schema.schema_message import MessageCreate, Message
from app.helper.enum import typeChatRoom, typeMessage, typeUser
from app.schema.schema_user import UserBase, User
from app.core.user.service_user import set_user_active, get_user_by_id
from app.crud.userCRUD import get_by_id
from app.core.chatRoom.websocket_chat_room import broadcast_json as broadcast_json_chat_room

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.rooms: Dict[int, List[WebSocket]] = {}

    def get_connection(self, user_id: int):
        if user_id not in self.active_connections:
            return None
        return self.active_connections[user_id]
    
    def get_all_connection(self):
        if not self.active_connections:
            return None
        return self.active_connections
    
    def get_all_room(self):
        if not self.rooms:
            return None
        return self.rooms
    
    def get_room(self, chat_room_id: int):
        if chat_room_id not in self.rooms:
            return None
        return self.rooms[chat_room_id]
    
    def set_room(self, chat_room_id: int, websocket: WebSocket, db: Session):
        if chat_room_id not in self.rooms:
            self.rooms[chat_room_id] = []
            set_room_activity(chat_room_id, active=True, db=db)
        self.rooms[chat_room_id].append(websocket)
    
    def remove_websocket_room(self, chat_room_id: int, websocket: WebSocket, db: Session):
        self.rooms[chat_room_id].remove(websocket)
        if len(self.rooms[chat_room_id]) == 0:
            set_room_activity(chat_room_id, active=False, db=db)
            self.rooms.pop(chat_room_id)
    
    def remove_connection(self, user_id: int):
        self.active_connections.pop(user_id)

    async def connect(self, websocket: WebSocket, user_id: int, db: Session):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def disconnect(self, websocket: WebSocket, user_id: int, db: Session):
        self.active_connections.pop(user_id)
        try:
            user = get_by_id(user_id, db)
            if user:
                chat_rooms = user.chat_rooms
                for chat_room in chat_rooms:
                    chat_room_id = chat_room.id
                    response = remove_member_from_chat_room(chat_room.id, user_id, db)
                    print(user.id)
                    if response is not None:
                            response = jsonable_encoder({
                                "chat_room_id": chat_room_id,
                                "user": User(**user.__dict__)
                            })
                    if len(self.get_room(chat_room_id)) == 1:
                            self.remove_websocket_room(chat_room_id, websocket, db)
                            connections = self.get_all_connection()
                            if connections:
                                connections = connections.values()
                            else:
                                return
                            await broadcast_json_chat_room({"chat_room_id": chat_room_id}, typeChatRoom.INACTIVE, connections, db=db)
                    else:
                            self.remove_websocket_room(chat_room_id, websocket, db)
                            await broadcast_json_chat_room(response,typeChatRoom.LEAVE, self.get_room(chat_room_id), db=db)


        except Exception as e:
            print(e)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_personal_json(self, payload: dict, type_function, type_action, websocket: WebSocket):
        payload_json = jsonable_encoder(payload)
        payload = {
            "type_function": type_function,
            "type_action": type_action,
            "payload": payload_json,
        }
        await websocket.send_json(payload)

    async def broadcast(self, type_functions, type_action,message: str, db: Session):
        try:
            if not self.active_connections:
                return
            
            for connection in self.active_connections.values():
                await connection.send_text(message)
        except Exception as e:
            print(e)
            
    async def broadcast_json(self,type_function, type_action, data: dict, db: Session):
        try:
            if not self.active_connections:
                return
            
            payload_json = jsonable_encoder(data)
            
            payload = {
                    "type_function": type_function,
                    "type_action": type_action,
                    "payload": payload_json,
                }

            for connection in self.active_connections.values():
                await connection.send_json(payload)
        except Exception as e:
            print(e)
    
connection_manager = ConnectionManager()