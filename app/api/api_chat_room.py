import json
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.db.base import get_db
from app.helper.enum import constant
from app.core.chatRoom import service_chat_room
from app.core.auth.service_auth import get_current_user
from app.schema.schema_user import User


router = APIRouter()

@router.get("")
@router.post("")
@router.put("")
@router.delete("")
def handle(
    request: Request,
    data: dict = {},
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    args = {item[0]: item[1] for item in request.query_params.multi_items()}
    if request.method == "GET":
        id = args.get("id", None)
        filter_member = args.get("filter_member", False)
        fiter_message = args.get("filter_message", False)
        if filter_member:
            status, status_code, response = service_chat_room.get_chat_room_member_by_chat_room_id(id, db)
        elif fiter_message:
            status, status_code, response = service_chat_room.get_chat_room_message_by_chat_room_id(id, db)
        elif id:
            status, status_code, response = service_chat_room.get_chat_room_by_id(id, db)
        else:
            status, status_code, response = service_chat_room.get_all_chat_room(db)
    elif request.method == "POST":
        status, status_code, response = service_chat_room.create_chat_room({**args, **data}, current_user.id, db)
    elif request.method == "DELETE":
        id = args.get("id", None)
        status, status_code, response = service_chat_room.delete_chat_room(current_user, id, db)

    if status == constant.ERROR:
        raise HTTPException(status_code=status_code, detail=response)
    elif status == constant.SUCCESS:
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(response)
        )

