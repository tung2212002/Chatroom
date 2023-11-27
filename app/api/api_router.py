from fastapi import APIRouter
from app.api import api_user, api_project, api_mange_project, api_auth, api_chat_room, api_message, api_manage_chat_room, api_websocket

router = APIRouter()

router.include_router(api_mange_project.router, prefix="/project/manage", tags=["project-manage"])
router.include_router(api_project.router, prefix="/project", tags=["project"])
router.include_router(api_user.router, prefix="/user", tags=["user"])
router.include_router(api_auth.router, prefix="/auth", tags=["auth"])
router.include_router(api_manage_chat_room.router, prefix="/chatroom/manage", tags=["chat-room-manage"])
router.include_router(api_chat_room.router, prefix="/chatroom", tags=["chat-room"])
router.include_router(api_websocket.router, tags=["websocket"])
router.include_router(api_message.router, tags=["message"])
