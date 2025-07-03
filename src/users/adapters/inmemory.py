from typing import override
import uuid

from src.users.domain import ports, entities, valueobjects


class UserStorage(ports.UserAdder, ports.UserFinderByUsername):
    def __init__(self):
        self.users: dict[uuid.UUID, entities.User] = dict()
        self.names_to_id: dict[str, uuid.UUID] = dict()

    @override
    async def find_by_username(self, username: valueobjects.Username) -> entities.User:
        if username.value not in self.names_to_id.keys():
            raise ports.NotFoundError("user", "username")

        user_id = self.names_to_id[username.value]
        if user_id not in self.users.keys():
            raise ports.NotFoundError("user", "username")

        return self.users[user_id]

    @override
    async def add(self, user: entities.User):
        if user.username.value in self.names_to_id.keys():
            raise ports.DuplicationError("user", "username", user.username.value)
        if user.id in self.users.keys():
            raise ports.DuplicationError("user", "id", user.id)
        self.users[user.id] = user
        self.names_to_id[user.username.value] = user.id


class SessionStorage(
    ports.SessionAdder, ports.SessionUpdater, ports.SessionFinderByToken
):
    def __init__(self):
        self.sessions: dict[uuid.UUID, entities.Session] = dict()
        self.token_session: dict[str, uuid.UUID] = dict()

    @override
    async def add(self, session: entities.Session):
        if session.token in self.token_session:
            raise ports.DuplicationError("session", "token", session.token)
        if session.id in self.sessions:
            raise ports.DuplicationError("session", "id", session.id)

        self.sessions[session.id] = session
        self.token_session[session.token] = session.id

    @override
    async def update(self, session: entities.Session):
        pass

    @override
    async def find_by_token(self, token: str) -> entities.Session:
        if token not in self.token_session:
            raise ports.NotFoundError("session", "token")
        id = self.token_session[token]
        if id not in self.token_session:
            raise ports.NotFoundError("session", "token")
        session = self.sessions[id]

        if session.has_expired():
            self.__check_and_delete(session)
        return session

    def __check_and_delete(self, session: entities.Session):
        _ = self.sessions.pop(session.id)
        _ = self.token_session.pop(session.token)
