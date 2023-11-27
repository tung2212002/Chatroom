from sqlalchemy.orm import Session
from app.core.security import get_password_hash

from app.model.user import User
from app.schema.schema_user import UserCreate, UserUpdate


def get_by_id(id: int, db: Session):
    return db.query(User).filter(User.id == id).first()


def get_all_users(db: Session):
    return db.query(User).all()


def get_by_username(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()


def create(user: UserCreate, db: Session):
    hash_password = get_password_hash(user["password"])
    db_user = User(
        username=user["username"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        hashed_password=hash_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update(username: str, user: UserUpdate, db: Session):
    db_user = get_by_username(username, db)
    db_user.first_name = user["first_name"]
    db_user.last_name = user["last_name"]
    db.commit()
    db.refresh(db_user)
    return db_user


def delete(username: str, db: Session):
    db_user = get_by_username(username, db)
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

def set_active(id: int, is_active: bool, db: Session):
    db_user = get_by_id(id, db)
    db_user.is_active = is_active
    db.commit()
    db.refresh(db_user)
    return db_user