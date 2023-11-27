from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends

from app.helper.enum import constant
from app.crud import userCRUD
from app.core.security import pwd_context
from app.core.config import settings
from app.schema.schema_user import UserLogin, User, UserBase
from app.core.security import oauth2
from app.crud import userCRUD
from app.db.base import get_db
from app.core.auth.auth_bearer import JWTBearer, JWTBearerWebSocket
from app.core.auth.auth_handler import signJWT, verify_token, decodeJWT

def authenticate(data: dict, db: Session):
    try:
        user = UserLogin(**data)
    except Exception as e:
        error = [f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()]
        return constant.ERROR, 400, error
    user = userCRUD.get_by_username(data["username"], db)
    if not user:
        return constant.ERROR, 404, "User not found"
    if not verify_password(data["password"], user.hashed_password):
        return constant.ERROR, 401, "Incorrect password"
    access_token = signJWT(user.username, user.id)
    refresh_token = signJWT(user.username, user.id)
    user = User(**user.__dict__)
    response = (
        constant.SUCCESS,
        200,
        {"access_token": access_token, "refresh_token": refresh_token , "user": user}
    )
    return response


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def get_current_active_user(username: str):
    pass


def get_current_user(token_decode: dict = Depends(JWTBearer()), db: Session = Depends(get_db)):
    username = token_decode["username"]
    user = userCRUD.get_by_username(username, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# def get_current_user_web_socket(token_decode: dict = Depends(JWTBearerWebSocket()), db: Session = Depends(get_db)):
#     username = token_decode["username"]
#     user = userCRUD.get_by_username(username, db)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

def get_current_user_web_socket(access_token: str, db):
    token_decode = check_veryfy_token(access_token)
    user_id = token_decode["user_id"]
    user = userCRUD.get_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def check_veryfy_token(token: str):
    token_decode = decodeJWT(token)
    exp = token_decode["exp"]
    now = datetime.utcnow()
    if now > datetime.fromtimestamp(exp):
        raise HTTPException(status_code=401, detail="Token expired")
    return token_decode
    


def refresh_token(data: dict, current_user, db: Session):
    access_token = signJWT(current_user.username, current_user.id)
    user = UserBase(**current_user.__dict__)
    response = (
        constant.SUCCESS,
        200,
        {"access_token": access_token, "user": user}
    )
    return response


