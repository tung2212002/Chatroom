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


ACCESS_TOKEN_EXPIRE = settings.ACCESS_TOKEN_EXPIRE
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.SECURITY_ALGORITHM


def signJWT(username: str, user_id: int):
    iat = datetime.utcnow()
    exp = iat + timedelta(seconds=ACCESS_TOKEN_EXPIRE)
    payload = {"username": username, "user_id": user_id, "iat": iat, "exp": exp}
    access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return access_token


def decodeJWT(token: str):

    try:
        decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decode_token
    except:
        return {}

def verify_token(data: dict, current_user, db: Session):
    user = User(**current_user.__dict__)
    response = constant.SUCCESS, 200, user
    return response


