from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    email: EmailStr
    subscribed_to_chat: bool = False

    class Config:
        allow_population_by_field_name = True


class Message(BaseModel):
    sender: str
    from_admin: bool
    text: str
    timestamp: datetime
