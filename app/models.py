from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    subscribed_to_chat: bool = False


class Message(BaseModel):
    sender: str
    from_admin: bool
    text: str
    timestamp: datetime
