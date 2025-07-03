import datetime
import uuid
from dataclasses import dataclass


from src.users.domain import ports, services, entities, valueobjects
from src.users.domain.errors import (
    InternalError,
    ValidationError,
    InvalidCredentials,
    MultiValidationErrors,
)


@dataclass
class Credentials:
    username: str
    password: str


@dataclass
class TokenSet:
    access_token: str
    refresh_token: str
    refresh_expires_at: datetime.datetime


class __AuthUseCase:
    def __init__(
        self,
        session_adder: ports.SessionAdder,
        refresh_generator: services.RefreshTokenGenerator,
        access_generator: services.AccessTokenGenerator,
        session_duration: datetime.timedelta,
        access_duration: datetime.timedelta,
    ):
        self.__session_adder = session_adder
        self.__refresh_gen = refresh_generator
        self.__access_gen = access_generator
        self.__session_duration = session_duration
        self.__access_duration = access_duration

    @staticmethod
    def _validate_request(
        request: Credentials,
    ) -> tuple[valueobjects.Username, valueobjects.Password]:
        username: valueobjects.Username | None = None
        password: valueobjects.Password | None = None

        validation_errors: list[ValidationError] = []

        try:
            username = valueobjects.Username(request.username)
        except ValidationError as ve:
            validation_errors.append(ve)

        try:
            password = valueobjects.Password(request.password)
        except ValidationError as ve:
            validation_errors.append(ve)

        if len(validation_errors) > 1:
            raise MultiValidationErrors(validation_errors)
        elif len(validation_errors) == 1:
            raise validation_errors[0]

        assert username is not None
        assert password is not None

        return username, password

    async def _create_session(self, user: uuid.UUID) -> TokenSet:
        session = entities.Session.new(
            self.__refresh_gen.generate_token(), user, self.__session_duration
        )
        try:
            await self.__session_adder.add(session)
        except Exception as e:
            raise InternalError() from e

        access_token = self.__access_gen.generate_token(
            user, session.created_at + self.__access_duration
        )
        return TokenSet(
            access_token,
            refresh_token=session.token,
            refresh_expires_at=session.expires_at,
        )


class RegisterUseCase(__AuthUseCase):
    def __init__(
        self,
        user_adder: ports.UserAdder,
        session_adder: ports.SessionAdder,
        refresh_generator: services.RefreshTokenGenerator,
        access_generator: services.AccessTokenGenerator,
        session_duration: datetime.timedelta,
        access_duration: datetime.timedelta,
    ):
        super().__init__(
            session_adder,
            refresh_generator,
            access_generator,
            session_duration,
            access_duration,
        )
        self.__user_adder = user_adder

    async def execute(self, request: Credentials) -> TokenSet:
        username, password = self._validate_request(request)
        user = entities.User.new(username, password)

        try:
            await self.__user_adder.add(user=user)
        except Exception as e:
            raise InternalError() from e

        return await self._create_session(user.id)


class LoginUseCase(__AuthUseCase):
    def __init__(
        self,
        user_finder: ports.UserFinderByUsername,
        session_adder: ports.SessionAdder,
        refresh_generator: services.RefreshTokenGenerator,
        access_generator: services.AccessTokenGenerator,
        session_duration: datetime.timedelta,
        access_duration: datetime.timedelta,
    ):
        super().__init__(
            session_adder,
            refresh_generator,
            access_generator,
            session_duration,
            access_duration,
        )
        self.__user_finder = user_finder

    async def execute(self, request: Credentials) -> TokenSet:
        username, _ = self._validate_request(request)
        user = None
        try:
            user = await self.__user_finder.find_by_username(username)
        except Exception as e:
            raise InternalError() from e

        if not user.password.compare(request.password):
            raise InvalidCredentials()

        return await self._create_session(user.id)


class RefreshSessionUseCase:
    def __init__(
        self,
        session_finder: ports.SessionFinderByToken,
        session_updater: ports.SessionUpdater,
        refresh_generator: services.RefreshTokenGenerator,
        access_generator: services.AccessTokenGenerator,
        session_duration: datetime.timedelta,
        access_duration: datetime.timedelta,
    ):
        self.__finder = session_finder
        self.__updater = session_updater
        self.__refresh_gen = refresh_generator
        self.__access_gen = access_generator
        self.__session_duration = session_duration
        self.__access_duration = access_duration

    async def execute(self, old_refresh_token: str) -> TokenSet:
        try:
            session = await self.__finder.find_by_token(old_refresh_token)

            new_token = self.__refresh_gen.generate_token()
            session.refresh(new_token, self.__session_duration)

            await self.__updater.update(session)

            access_token = self.__access_gen.generate_token(
                session.user, session.refreshed_at + self.__access_duration
            )
            return TokenSet(
                access_token,
                refresh_token=session.token,
                refresh_expires_at=session.expires_at,
            )
        except Exception as e:
            raise InternalError() from e


class RefreshAccessUseCase:
    def __init__(
        self,
        session_finder: ports.SessionFinderByToken,
        access_generator: services.AccessTokenGenerator,
        access_duration: datetime.timedelta,
    ):
        self.__finder = session_finder
        self.__generator = access_generator
        self.__duration = access_duration

    async def execute(self, refresh: str) -> str:
        try:
            session = await self.__finder.find_by_token(refresh)
            expires_at = datetime.datetime.now() + self.__duration
            return self.__generator.generate_token(session.user, expires_at)
        except Exception as e:
            raise InternalError() from e
