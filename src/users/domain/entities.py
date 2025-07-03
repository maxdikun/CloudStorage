import datetime
import uuid

from src.users.domain.valueobjects import Username, Password


class User:
    def __init__(
        self,
        id: uuid.UUID,
        username: Username,
        password: Password,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        is_deleted: bool,
    ) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_deleted = is_deleted

    @staticmethod
    def new(username: Username, password: Password) -> "User":
        return User(
            uuid.uuid4(),
            username,
            password,
            datetime.datetime.now(),
            datetime.datetime.now(),
            False,
        )


class Session:
    def __init__(
        self,
        id: uuid.UUID,
        token: str,
        user: uuid.UUID,
        created_at: datetime.datetime,
        refreshed_at: datetime.datetime,
        expires_at: datetime.datetime,
    ) -> None:
        self.id = id
        self.token = token
        self.user = user
        self.created_at = created_at
        self.refreshed_at = refreshed_at
        self.expires_at = expires_at

    def refresh(self, token: str, duration: datetime.timedelta):
        self.token = token
        self.refreshed_at = datetime.datetime.now()
        self.expires_at = datetime.datetime.now() + duration

    def has_expired(self) -> bool:
        return datetime.datetime.now() > self.expires_at

    @staticmethod
    def new(token: str, user: uuid.UUID, duration: datetime.timedelta) -> "Session":
        return Session(
            uuid.uuid4(),
            token,
            user,
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now() + duration,
        )
