from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.core.schemas import ApiModel


class LoginRequest(ApiModel):
    username: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=1, max_length=72)


class UserView(ApiModel):
    id: UUID
    username: str


class SessionView(ApiModel):
    user: UserView
    expires_at: datetime


class RefreshView(ApiModel):
    expires_at: datetime
