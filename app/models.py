"""Pydantic schemas for API request and response validation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str | None = Field(default=None, examples=["Review Docker Compose setup"])
    done: bool | None = Field(default=False, examples=[False])


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, examples=["Ship completed assignment"])
    done: bool | None = Field(default=None, examples=[True])


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool


class ErrorResponse(BaseModel):
    error: str


class HealthResponse(BaseModel):
    status: str
    db: str


class AuthCredentials(BaseModel):
    email: str | None = Field(default=None, examples=["student@example.com"])
    password: str | None = Field(default=None, examples=["strong-password-123"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


class UserProfileResponse(BaseModel):
    id: str | None = None
    email: str | None = None
    created_at: str | None = None


class PublicInfoResponse(BaseModel):
    message: str


class DashboardResponse(BaseModel):
    status: str
    message: str
    user_id: str | None = None
