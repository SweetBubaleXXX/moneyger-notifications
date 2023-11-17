from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCredentials(BaseModel):
    token: str
    email: EmailStr


class UserSettings(BaseModel):
    subscribed_to_chat: bool = False


class User(UserCredentials, UserSettings):
    pass


class Message(BaseModel):
    sender: str
    from_admin: bool
    text: str
    timestamp: datetime
