from sqlalchemy.orm import Session

from app.core.security import pwd_context
from app.crud import userCRUD
from app.helper.enum import constant
from app.schema.schema_user import UserCreate, UserUpdate, UserBase, User
from app.core.auth.service_auth import signJWT


def get_user(username: str, db: Session):
    user = userCRUD.get_by_username(username, db)
    if not user:
        return constant.ERROR, 404, "User not found"
    user = User(**user.__dict__)
    return constant.SUCCESS, 200, user

def get_user_by_id(id: int, db: Session):
    user = userCRUD.get_by_id(id, db)
    if not user:
        return constant.ERROR, 404, "User not found"
    user = User(**user.__dict__)
    return constant.SUCCESS, 200, user


def create_user(data: dict, db: Session):
    try:
        user_data = UserCreate(**data)
    except Exception as e:
        error = [f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()]
        return constant.ERROR, 400, error

    user = userCRUD.get_by_username(data["username"], db)

    if user:
        return constant.ERROR, 400, "Username already registered"
    user = userCRUD.create(data, db)
    user = User(**user.__dict__)

    access_token = signJWT(user.username, user.id)
    refresh_token = signJWT(user.username, user.id)

    response = (
        constant.SUCCESS,
        201,
        {"access_token": access_token, "refresh_token": refresh_token, "user": user}
    )
    return response


def update_user(data: dict, current_user, db: Session):
    if current_user is None:
        return constant.ERROR, 401, "Unauthorized"
    if data["username"] != current_user.username:
        return constant.ERROR, 401, "Unauthorized"

    try:
        user = UserUpdate(**data)
    except Exception as e:
        error = [f'{error["loc"][0]}: {error["msg"]}' for error in e.errors()]
        return constant.ERROR, 400, error
    
    user_update = userCRUD.update(data["username"], data, db)
    user_update = User(**user_update.__dict__)
    response = (
        constant.SUCCESS,
        200,
        user_update
    )
    return response


def delete_user(username: str, current_user, db: Session):
    if current_user is None:
        return constant.ERROR, 401, "Unauthorized"
    if username != current_user.username:
        return constant.ERROR, 401, "Unauthorized"
    if username is None:
        return constant.ERROR, 400, "Username is required"
    response = constant.SUCCESS, 200, userCRUD.delete(username, db)
    return response

def set_user_active(id: int, active: bool, db: Session):
    if id is None:
        return constant.ERROR, 400, "Id is required"
    response = constant.SUCCESS, 200, userCRUD.set_active(id, active, db)
    return response


