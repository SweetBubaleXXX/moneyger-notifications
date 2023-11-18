from abc import ABCMeta, abstractmethod
from collections.abc import Collection, Iterator, Iterable
from typing import TypeVar, Generic, Callable, Any, Self

from redis import Redis
from redis.lock import Lock

from ..models import Message

T = TypeVar("T")


class MessageStorage(Collection, Generic[T], metaclass=ABCMeta):
    storage_size_limit: int | None
    on_storage_exhausted: Callable[[Self], Any] | None

    @abstractmethod
    def __init__(
        self, get_storage: Callable[..., T], storage_size_limit: int | None = None
    ) -> None:
        ...

    @abstractmethod
    def get_all(self) -> Iterable[Message]:
        ...

    @abstractmethod
    def push(self, message: Message) -> None:
        ...

    @abstractmethod
    def remove(self, message_id: str) -> None:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...


class RedisMessageStorage(MessageStorage):
    _MESSAGES_SET_KEY = "messages_set"
    _MESSAGE_KEY = "message:{id}"
    _LOCK_NAME = "messages_lock"
    _LOCK_TIMEOUT = 120
    _BLOCKING_TIMEOUT = 60

    def __init__(
        self, get_storage: Callable[..., Redis], storage_size_limit: int | None = None
    ):
        self._redis = get_storage()
        self.storage_size_limit = storage_size_limit
        self.on_storage_exhausted = None
        self._lock = Lock(
            self._redis,
            self._LOCK_NAME,
            timeout=self._LOCK_TIMEOUT,
            blocking_timeout=self._BLOCKING_TIMEOUT,
        )

    def __len__(self) -> int:
        return int(self._redis.zcard(self._MESSAGES_SET_KEY))

    def __contains__(self, message_id: str) -> bool:
        return self._redis.sismember(self._MESSAGES_SET_KEY, message_id)

    def __iter__(self) -> Iterator[Message]:
        return iter(self.get_all())

    def get_all(self) -> Iterable[Message]:
        with self._lock:
            messages = self._get_message_ids()
            loaded_messages = []
            for message_id in messages:
                raw_message = self._redis.hgetall(self._MESSAGE_KEY.format(message_id))
                parsed_message = Message.parse_obj(raw_message)
                loaded_messages.append(parsed_message)
            return loaded_messages

    def push(self, message: Message) -> None:
        message_key = self._MESSAGE_KEY.format(message.id)
        with self._lock:
            if len(self) == self.storage_size_limit:
                return self.on_storage_exhausted and self.on_storage_exhausted()
            self._redis.hset(message_key, mapping=message.dict())
            self._redis.zadd(
                self._MESSAGES_SET_KEY, {message.id: message.timestamp.timestamp()}
            )

    def remove(self, message_id: str) -> None:
        with self._lock:
            self._redis.zrem(self._MESSAGES_SET_KEY, message_id)
            self._redis.delete(self._MESSAGE_KEY.format(message_id))

    def clear(self) -> None:
        with self._lock:
            messages = self._get_message_ids()
            for message_id in messages:
                self._redis.delete(self._MESSAGE_KEY.format(message_id))
            self._redis.delete(self._MESSAGES_SET_KEY)

    def _get_message_ids(self) -> Iterable[str]:
        return self._redis.zrange(self._MESSAGES_SET_KEY, 0, -1)
