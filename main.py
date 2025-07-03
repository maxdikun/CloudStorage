import uvicorn
import datetime

from fastapi import FastAPI

from src.users.adapters import inmemory
from src.users.adapters.routes import (
    auth_router,
    login_use_case,
    refresh_access_use_case,
    refresh_session_use_case,
    register_use_case,
)
from src.users.domain import usecases, services

users = inmemory.UserStorage()
sessions = inmemory.SessionStorage()
refresh_gen = services.RefreshTokenGenerator()
access_gen = services.AccessTokenGenerator("complex_secret")

session_duration = datetime.timedelta(hours=24)
access_duration = datetime.timedelta(hours=2)

app = FastAPI()

app.dependency_overrides[register_use_case] = lambda: usecases.RegisterUseCase(
    users, sessions, refresh_gen, access_gen, session_duration, access_duration
)

app.dependency_overrides[login_use_case] = lambda: usecases.LoginUseCase(
    users, sessions, refresh_gen, access_gen, session_duration, access_duration
)

app.dependency_overrides[refresh_session_use_case] = (
    lambda: usecases.RefreshSessionUseCase(
        sessions, sessions, refresh_gen, access_gen, session_duration, access_duration
    )
)

app.dependency_overrides[refresh_access_use_case] = (
    lambda: usecases.RefreshAccessUseCase(sessions, access_gen, access_duration)
)


app.include_router(auth_router, prefix="/api/auth")

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
