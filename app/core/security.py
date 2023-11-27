from fastapi.security import HTTPBearer
from passlib.context import CryptContext

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2 = HTTPBearer(
    scheme_name="Authorization",
)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

