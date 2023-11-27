import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime
import uuid

from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.auth.service_auth import get_current_user, get_current_user_web_socket
from app.helper.enum import constant
from app.core.chatRoom import service_chat_room
from app.core.message import service_message
from app.model.user import User
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer

from app.core.auth.service_auth import get_current_user_web_socket
from app.core.chatRoom.service_chat_room import get_chat_room_by_id, add_member_to_chat_room, remove_member_from_chat_room
from app.core.message.service_message import create_message, get_all_message
from app.core.manage_websocket import connection_manager
from app.helper.enum import typeSendChatRoom, typeMessage
from app.core.message.websocket_message import handle_message
from app.core.chatRoom.websocket_chat_room import handle_chat_room
from app.core.user.websocket_user import handle_user
from app.helper.enum import typeUser, typeFunction

router = APIRouter()

list_websocket = []
max = 0

@router.websocket("/ws/checkconnection/{id}")
# async def websocket_endpoint(websocket: WebSocket, chat_room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_web_socket)):
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    print(websocket.client_state)
    list_websocket.append(websocket)
    is_connection = True
    try:
        while is_connection:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        is_connection = False
    finally:
        try:
            # pass
            if is_connection:
                await websocket.close()
        except Exception as e:
            print("Exception")
            

@router.websocket("/ws/chatroom/{chat_room_id}")
# async def websocket_endpoint(websocket: WebSocket, chat_room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_web_socket)):
async def websocket_endpoint(websocket: WebSocket, chat_room_id: int, db: Session = Depends(get_db)):
    prams = websocket.query_params
    access_token = prams.get("access_token")
    current_user = get_current_user_web_socket(access_token, db)
    await connection_manager.connect(websocket, chat_room_id, current_user.id, db)
    is_connection = True
    await connection_manager.broadcast(f"{current_user.last_name} {current_user.first_name} has joined the chat", typeSendChatRoom.ROOM, chat_room_id, current_user, db)
    try:
        while is_connection:
            data = await websocket.receive_json()
            message = data.get("content", None)
            type = data.get("type", None)
            id = data.get("id", None)
            if type == typeMessage.CREATE:
                status, status_code, response = create_message(message, current_user, chat_room_id, db)
                await connection_manager.broadcast_json(response,typeMessage.CREATE, chat_room_id, current_user, db)
            elif type == typeMessage.DELETE:
                status, status_code, response = service_message.delete_message(current_user, id, db)
                await connection_manager.broadcast_json(response,typeMessage.DELETE, chat_room_id, current_user, db)
            
    except WebSocketDisconnect:
        is_connection = False
    finally:
        await connection_manager.disconnect(websocket, chat_room_id, current_user.id, db)
        await connection_manager.broadcast(f"{current_user.last_name} {current_user.first_name} has left the chat", typeSendChatRoom.ROOM, chat_room_id, current_user, db)
        try:
            status = websocket.client_state
            if is_connection:
                await websocket.close()
        except Exception as e:
            print(e)


@router.websocket("/ws/test")
# async def websocket_endpoint(websocket: WebSocket, chat_room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_web_socket)):
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):

    prams = websocket.query_params
    access_token = prams.get("access_token")
    current_user = get_current_user_web_socket(access_token, db)
    fake_id = uuid.uuid4()
    current_user.id = fake_id
    connection = connection_manager.get_connection(current_user.id)
    if connection is None:
        await connection_manager.connect(websocket, current_user.id, db)       
    is_connection = True
    try:
        while is_connection:
            data = await websocket.receive_json()
            type_function = data.get("type_function", None)
            type_action = data.get("type_action", None)
            payload = data.get("payload", None)
            if not type_function:
                websocket.send_text("Test")
            if type_function == typeFunction.MESSAGE:
                await handle_message(websocket, connection_manager, type_action, payload, current_user, db)
            elif type_function == typeFunction.CHAT_ROOM:
                await handle_chat_room(websocket,connection_manager, type_action, payload, current_user, db)                

    except WebSocketDisconnect:
        is_connection = False
    finally:
        await connection_manager.disconnect(websocket, current_user.id, db)
        await connection_manager.broadcast_json(typeFunction.USER, typeUser.OFFLINE, data = {"user": current_user}, db=db)
        try:
            if is_connection:
                await websocket.close()
        except Exception as e:
            print(e)

