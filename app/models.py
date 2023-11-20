from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCredentials(BaseModel):
    account_id: int
    email: EmailStr
    token: str


class UserSettings(BaseModel):
    subscribed_to_chat: bool = False


class User(UserCredentials, UserSettings):
    pass


class Message(BaseModel):
    sender: str
    from_admin: bool
    text: str
    timestamp: datetime
