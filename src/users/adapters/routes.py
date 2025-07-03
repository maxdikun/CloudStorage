import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.users.domain import usecases


class TokenSet(BaseModel):
    access_token: str
    refresh_token: str
    refresh_expires_at: datetime.datetime


class Credentials(BaseModel):
    username: str
    password: str


def register_use_case() -> usecases.RegisterUseCase:
    raise NotImplementedError()


def login_use_case() -> usecases.RegisterUseCase:
    raise NotImplementedError()


def refresh_session_use_case() -> usecases.RefreshSessionUseCase:
    raise NotImplementedError()


def refresh_access_use_case() -> usecases.RefreshAccessUseCase:
    raise NotImplementedError()


auth_router = APIRouter()


@auth_router.post(
    "/register",
    summary="Register a new user",
)
async def register(
    request: Credentials,
    use_case: usecases.RegisterUseCase = Depends(register_use_case),
) -> TokenSet:
    try:
        result = await use_case.execute(
            usecases.Credentials(request.username, request.password)
        )

        return TokenSet(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            refresh_expires_at=result.refresh_expires_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.__str__(),
        )


@auth_router.post("/login", summary="Log in account")
async def login(
    request: Credentials, use_case: usecases.LoginUseCase = Depends(login_use_case)
):
    try:
        result = await use_case.execute(
            usecases.Credentials(request.username, request.password)
        )

        return TokenSet(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            refresh_expires_at=result.refresh_expires_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.__str__(),
        )
