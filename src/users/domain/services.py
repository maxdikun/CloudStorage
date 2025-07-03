import datetime
import secrets
import uuid

import jwt


class RefreshTokenGenerator:
    def __init__(self) -> None:
        pass

    def generate_token(self) -> str:
        return secrets.token_hex(64)


class AccessTokenGenerator:
    def __init__(self, secret: str, algorithm: str = "HS256") -> None:
        self.__secret = secret
        self.__algo = algorithm

    def generate_token(self, sub: uuid.UUID, expires_at: datetime.datetime) -> str:
        payload = {
            "sub": sub.__str__(),
            "exp": expires_at,
            "iat": datetime.datetime.now(),
            "iss": "cloud-storage-app",
        }

        return jwt.encode(payload, key=self.__secret, algorithm=self.__algo)
