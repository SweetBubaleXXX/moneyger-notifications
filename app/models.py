from datetime import datetime
from decimal import Decimal
from typing import Literal, Self, Type, TypeAlias, TypeVar

from pydantic import BaseModel, EmailStr

T = TypeVar("T", bound=BaseModel, covariant=True)

TransactionType: TypeAlias = Literal["IN", "OUT"]


class UserCredentials(BaseModel):
    account_id: int
    email: EmailStr
    token: str


class UserSettings(BaseModel):
    subscribed_to_chat: bool = False
    subscribed_to_predictions: bool = False


class User(UserCredentials, UserSettings):
    @property
    def credentials(self) -> UserCredentials:
        return self._construct_model(UserCredentials)

    @property
    def settings(self) -> UserSettings:
        return self._construct_model(UserSettings)

    def copy_with_updated_settings(self, settings: UserSettings) -> Self:
        updated_user = self.copy()
        for field, value in settings:
            updated_user.__setattr__(field, value)
        return updated_user

    def _construct_model(self, model: Type[T]) -> T:
        common_fields = self.dict(include=model.__fields__.keys())
        return model.construct(**common_fields)


class JwtTokenPayload(BaseModel):
    account_id: int


class UserCredentialsResponse(BaseModel):
    success: bool
    result: UserCredentials | None


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


class Transaction(BaseModel):
    account_id: int
    transaction_id: int
    transaction_type: TransactionType
    amount: Decimal
    transaction_time: datetime
