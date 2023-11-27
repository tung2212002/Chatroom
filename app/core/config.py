import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "FASTAPI BASE")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    API_PREFIX: str = ""
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    DATABASE_URL: str = os.getenv("SQLALCHEMY_DATABASE_URL", "")
    ACCESS_TOKEN_EXPIRE: int = os.getenv("ACCESS_TOKEN_EXPIRES_IN")
    REFRESH_TOKEN_EXPIRE: int = os.getenv("REFRESH_TOKEN_EXPIRES_IN")
    SECURITY_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")


settings = Settings()
