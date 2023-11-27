from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.db.base import get_db
from app.core.auth.service_auth import get_current_user 
from app.helper.enum import constant
from app.core.user import service_user

router = APIRouter()

@router.get("")
@router.post("")
@router.put("")
@router.delete("")
def handle(
    request: Request,
    data: dict = {},
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    args = {item[0]: item[1] for item in request.query_params.multi_items()}
    if request.method == "GET":
        username = args.get("username", None)
        status, status_code, response = service_user.get_user(username, db)
    elif request.method == "PUT":
        status, status_code, response = service_user.update_user({**args, **data}, current_user, db)
    elif request.method == "DELETE":
        username = args.get("username", None)        
        status, status_code, response = service_user.delete_user(username, current_user, db)

    if status == constant.ERROR:
        raise HTTPException(status_code=status_code, detail=response)
    elif status == constant.SUCCESS:
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(response)
        )
