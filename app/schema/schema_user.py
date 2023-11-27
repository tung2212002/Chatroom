from pydantic import BaseModel, ConfigDict, Field, validator

class UserBase(BaseModel):
    username: str 
    first_name: str
    last_name: str

    @validator("username")
    def username_alphanumeric(cls, v):
        if len(v) < 3:
            raise ValueError("username must be at least 3 characters")
        if not v.isalnum():
            raise ValueError("username must be alphanumeric")
        return v
    @validator("first_name")
    def first_name_alphabetic(cls, v):
        if not v.isalpha():
            raise ValueError("first name must be alphabetic")
        return v
    @validator("last_name")
    def last_name_alphabetic(cls, v):
        if not v.isalpha():
            raise ValueError("last name must be alphabetic")
        return v
        
class UserCreate(UserBase):
    password: str

    @validator("password")
    def password_alphanumeric(cls, v):
        if len(v) < 6:
            raise ValueError("password must be at least 6 characters")
        return v

class UserUpdate(BaseModel):
    first_name: str
    last_name: str

    @validator("first_name")
    def first_name_alphabetic(cls, v):
        if not v.isalpha():
            raise ValueError("first name must be alphabetic")
        return v
    @validator("last_name")
    def last_name_alphabetic(cls, v):
        if not v.isalpha():
            raise ValueError("last name must be alphabetic")
        return v
    
class UserLogin(BaseModel):
    username: str
    password: str

    @validator("username")
    def username_alphanumeric(cls, v):
        if len(v) < 3:
            raise ValueError("username must be at least 3 characters")
        if not v.isalnum():
            raise ValueError("username must be alphanumeric")
        return v
    @validator("password")
    def password_alphanumeric(cls, v):
        if len(v) < 6:
            raise ValueError("password must be at least 6 characters")
        return v


class User(UserBase):
    model_config = ConfigDict(from_attribute=True)

    id: int
    is_active: bool
    picture_path: str

    
