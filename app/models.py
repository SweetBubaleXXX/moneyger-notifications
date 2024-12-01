from datetime import datetime
from decimal import Decimal
from typing import Literal, TypeAlias, TypeVar

from pydantic import BaseModel, EmailStr

T = TypeVar("T", bound=BaseModel, covariant=True)

TransactionType: TypeAlias = Literal["IN", "OUT"]


class User(BaseModel):
    account_id: int
    email: EmailStr
    is_admin: bool = False


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
