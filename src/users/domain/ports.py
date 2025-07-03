from abc import ABC, abstractmethod

from src.users.domain import entities, valueobjects


class NotFoundError(Exception):
    def __init__(self, object: str, field: str):
        self.object = object
        self.field = field


class DuplicationError(Exception):
    def __init__(self, object: str, field: str, value):
        self.object = object
        self.field = field
        self.value = value


class UserAdder(ABC):
    @abstractmethod
    async def add(self, user: entities.User):
        raise NotImplementedError()


class UserFinderByUsername(ABC):
    @abstractmethod
    async def find_by_username(self, username: valueobjects.Username) -> entities.User:
        raise NotImplementedError()


class SessionAdder(ABC):
    @abstractmethod
    async def add(self, session: entities.Session):
        raise NotImplementedError()


class SessionFinderByToken(ABC):
    @abstractmethod
    async def find_by_token(self, token: str) -> entities.Session:
        raise NotImplementedError()


class SessionUpdater(ABC):
    @abstractmethod
    async def update(self, session: entities.Session):
        raise NotImplementedError()
