import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime

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
from app.helper.enum import typeSendChatRoom, typeMessage, typeUser, typeFunction
from app.core.message.websocket_message import handle_message
from app.core.chatRoom.websocket_chat_room import handle_chat_room
from app.core.user.websocket_user import handle_user

router = APIRouter()

@router.websocket("/ws/connect")
# async def websocket_endpoint(websocket: WebSocket, chat_room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_web_socket)):
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):

    prams = websocket.query_params
    access_token = prams.get("access_token")
    current_user = get_current_user_web_socket(access_token, db)
    connection = connection_manager.get_connection(current_user.id)
    if connection is None:
        await connection_manager.connect(websocket, current_user.id, db)       
    is_connection = True
    await handle_user(connection_manager, typeUser.ONLINE, {"user": current_user}, current_user, db)
    await handle_user(connection_manager, typeUser.ALL, {"user": current_user}, current_user, db)
    try:
        while is_connection:
            data = await websocket.receive_json()
            type_function = data.get("type_function", None)
            type_action = data.get("type_action", None)
            payload = data.get("payload", None)
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

