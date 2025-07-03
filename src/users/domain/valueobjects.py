from typing import override
import bcrypt

from src.users.domain.errors import ValidationError


class Username:
    def __init__(self, value: str) -> None:
        if len(value) < 3:
            raise ValidationError("username", "should be at least 3 characters long")
        self.__value = value

    @property
    def value(self) -> str:
        return self.__value


class Password:
    def __init__(self, plaintext: str | None = None, hashed: str | None = None):
        if (plaintext is None and hashed is None) or (
            plaintext is not None and hashed is not None
        ):
            raise ValueError(
                "Either one of the plaintext or hashed argument should be provided."
            )

        if hashed is not None:
            if not (
                hashed.startswith("$2a$")
                or hashed.startswith("$2b$")
                or hashed.startswith("$2y$")
            ):
                raise ValueError(
                    "Hashed password format is invalid. Expected a bcrypt hash."
                )
            self.__value = hashed
            return

        if plaintext is not None:
            if len(plaintext) < 6:
                raise ValidationError(
                    "password", "should be at least 6 characters long"
                )

            salt = bcrypt.gensalt()
            full_hashed_bytes = bcrypt.hashpw(plaintext.encode("utf-8"), salt)
            self.__value = full_hashed_bytes.decode("utf-8")
            return

    @property
    def value(self):
        return self.__value

    def compare(self, plaintext_candidate: str) -> bool:
        return bcrypt.checkpw(
            plaintext_candidate.encode("utf-8"), self.__value.encode("utf-8")
        )

    @override
    def __repr__(self):
        return f"Password(hashed='{self.value}')"

