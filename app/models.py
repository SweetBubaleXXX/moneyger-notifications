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


class JwtTokenPayload(BaseModel):
    account_id: int


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
