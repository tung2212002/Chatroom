from pydantic import BaseModel, ConfigDict
from app.schema.schema_user import User

class ChatRoomBase(BaseModel):
    name: str
    description: str = None

class ChatRoomCreate(ChatRoomBase):
    pass

class ChatRoom(ChatRoomBase):
    model_config = ConfigDict(from_attribute=True)
    
    id: int
    owner_id: int
    members: list[User] = []

    
