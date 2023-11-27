from pydantic import BaseModel, ConfigDict

from datetime import datetime
from app.schema.schema_user import User

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    model_config = ConfigDict(from_attribute=True)

    id: int
    chat_room_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: User
   