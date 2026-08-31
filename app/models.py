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

