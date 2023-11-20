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
    id: str
    sender: str
    from_admin: bool
    text: str
    timestamp: datetime

    def __hash__(self) -> int:
        return hash(self.id)

    def dict_of_str(self) -> dict[str, str]:
        return {key: str(value) for key, value in self}
