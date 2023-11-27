from datetime import timedelta
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from app.db.base import get_db
from app.helper.enum import constant
from app.core.auth import service_auth
from app.schema.schema_user import User
from app.core.auth.service_auth import get_current_user, verify_token
from app.core.user import service_user

router = APIRouter()

@router.get("/verify-token")
def handle(request: Request, data: dict = {}, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    args = {item[0]: item[1] for item in request.query_params.multi_items()}
    if request.method == "GET":
        status, status_code, response = service_auth.verify_token({**args, **data}, current_user, db)

    if status == constant.ERROR:
        raise HTTPException(status_code=status_code, detail=response)
    elif status == constant.SUCCESS:
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(response)
        ) 

@router.post("/login")
def handle(request: Request, data: dict = {}, db: Session = Depends(get_db)):
    args = {item[0]: item[1] for item in request.query_params.multi_items()}
    status, status_code, response = service_auth.authenticate({**args, **data}, db)
    if status == constant.ERROR:
        raise HTTPException(status_code=status_code, detail=response)
    elif status == constant.SUCCESS:
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(response)
        )
    
@router.post("/register")
def handle(request: Request, data: dict = {}, db: Session = Depends(get_db)):
    args = {item[0]: item[1] for item in request.query_params.multi_items()}
    status, status_code, response = service_user.create_user({**args, **data}, db)
    if status == constant.ERROR:
        raise HTTPException(status_code=status_code, detail=response)
    elif status == constant.SUCCESS:
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(response)
        )
    
@router.get("/refresh-token")
def handle(request: Request, data: dict = {}, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    args = {item[0]: item[1] for item in request.query_params.multi_items()}
    if request.method == "GET":
        status, status_code, response = service_auth.refresh_token({**args, **data}, current_user, db)

    if status == constant.ERROR:
        raise HTTPException(status_code=status_code, detail=response)
    elif status == constant.SUCCESS:
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(response)
        )



