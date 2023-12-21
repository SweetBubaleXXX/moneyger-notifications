from abc import ABCMeta, abstractmethod
from collections.abc import Collection, Iterator
from typing import Any, Callable, Generic, Self, TypeVar

from redis import Redis
from redis.lock import Lock

from ..models import Message

T = TypeVar("T")


class MessageStorage(Collection, Generic[T], metaclass=ABCMeta):
    def __init__(self, storage: T, storage_size_limit: int) -> None:
        self.storage_size_limit = storage_size_limit
        self._storage = storage
        self._storage_exhausted_listeners: set[Callable[[Self], Any]] = set()

    @abstractmethod
    def get_all(self) -> Collection[Message]:
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

    def add_storage_exhausted_listener(self, callback: Callable[[Self], Any]) -> None:
        self._storage_exhausted_listeners.add(callback)

    def remove_storage_exhausted_listener(
        self, callback: Callable[[Self], Any]
    ) -> None:
        if callback in self._storage_exhausted_listeners:
            self._storage_exhausted_listeners.remove(callback)

    def _notify_storage_exhausted(self) -> None:
        for subscriber in self._storage_exhausted_listeners:
            subscriber(self)


class RedisMessageStorage(MessageStorage[Redis]):
    _MESSAGES_SET_KEY = "messages_set"
    _MESSAGE_KEY = "message:{id}"
    _LOCK_NAME = "messages_lock"
    _LOCK_TIMEOUT = 120
    _BLOCKING_TIMEOUT = 60

    def __init__(self, storage: Redis, storage_size_limit: int) -> None:
        super().__init__(storage, storage_size_limit)
        self._lock = Lock(
            self._storage,
            self._LOCK_NAME,
            timeout=self._LOCK_TIMEOUT,
            blocking_timeout=self._BLOCKING_TIMEOUT,
        )

    def __len__(self) -> int:
        return int(self._storage.zcard(self._MESSAGES_SET_KEY))

    def __contains__(self, message_id: object) -> bool:
        return bool(self._storage.zscore(self._MESSAGES_SET_KEY, message_id))

    def __iter__(self) -> Iterator[Message]:
        return iter(self.get_all())

    def get_all(self) -> Collection[Message]:
        with self._lock:
            messages = []
            for message_id in self._get_message_ids():
                parsed_message = self._get_message_by_id(message_id)
                messages.append(parsed_message)
            return messages

    def push(self, message: Message) -> None:
        message_key = self._MESSAGE_KEY.format(id=message.id)
        with self._lock:
            self._storage.hset(message_key, mapping=message.dict_of_str())
            self._storage.zadd(
                self._MESSAGES_SET_KEY, {message.id: message.timestamp.timestamp()}
            )
        if len(self) >= self.storage_size_limit:
            self._notify_storage_exhausted()

    def remove(self, message_id: str) -> None:
        with self._lock:
            self._storage.zrem(self._MESSAGES_SET_KEY, message_id)
            self._storage.delete(self._MESSAGE_KEY.format(id=message_id))

    def clear(self) -> None:
        with self._lock:
            messages = self._get_message_ids()
            for message_id in messages:
                self._storage.delete(self._MESSAGE_KEY.format(id=message_id))
            self._storage.delete(self._MESSAGES_SET_KEY)

    def _get_message_ids(self) -> Iterator[str]:
        raw_ids = self._storage.zrange(self._MESSAGES_SET_KEY, 0, -1)
        for raw_message_id in raw_ids:
            yield raw_message_id.decode()

    def _get_message_by_id(self, message_id: str) -> Message:
        raw_message = self._storage.hgetall(self._MESSAGE_KEY.format(id=message_id))
        decoded_message = {
            key.decode(): value.decode() for key, value in raw_message.items()
        }
        return Message.parse_obj(decoded_message)
