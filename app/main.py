"""FastAPI application definition and route declarations."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, Response, status
from fastapi.responses import JSONResponse

from app import database, repository
from app.models import ErrorResponse, HealthResponse, TaskCreate, TaskResponse, TaskUpdate


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    database.open_pool()
    repository.initialize_database()
    try:
        yield
    finally:
        database.close_pool()


app = FastAPI(
    title="FlyRank Week 1 A3 Task API",
    description="Containerized FastAPI and PostgreSQL task service.",
    version="1.0.0",
    lifespan=lifespan,
)


def _error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


def _clean_title(title: str | None) -> str | None:
    if title is None:
        return None

    cleaned = title.strip()
    return cleaned or None


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API and database health",
)
def health() -> dict[str, str]:
    repository.check_database()
    return {"status": "ok", "db": "ok"}


@app.get(
    "/tasks",
    response_model=list[TaskResponse],
    summary="List all tasks",
)
def list_tasks() -> list[dict]:
    return repository.list_tasks()


@app.get(
    "/tasks/{id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get a task by ID",
)
def get_task(id: int) -> dict | JSONResponse:
    task = repository.get_task(id)
    if task is None:
        return _error(status.HTTP_404_NOT_FOUND, "Task not found")
    return task


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
    summary="Create a task",
)
def create_task(payload: TaskCreate | None = Body(default=None)) -> dict | JSONResponse:
    title = _clean_title(payload.title if payload else None)
    if title is None:
        return _error(status.HTTP_400_BAD_REQUEST, "Title cannot be empty")

    done = bool(payload.done) if payload.done is not None else False
    return repository.create_task(title=title, done=done)


@app.put(
    "/tasks/{id}",
    response_model=TaskResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Update a task",
)
def update_task(id: int, payload: TaskUpdate | None = Body(default=None)) -> dict | JSONResponse:
    title = _clean_title(payload.title if payload else None)
    if title is None:
        return _error(status.HTTP_400_BAD_REQUEST, "Title cannot be empty")

    if payload.done is None:
        return _error(status.HTTP_400_BAD_REQUEST, "Done field is required")

    task = repository.update_task(task_id=id, title=title, done=payload.done)
    if task is None:
        return _error(status.HTTP_404_NOT_FOUND, "Task not found")
    return task


@app.delete(
    "/tasks/{id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Delete a task",
)
def delete_task(id: int) -> Response | JSONResponse:
    deleted = repository.delete_task(id)
    if not deleted:
        return _error(status.HTTP_404_NOT_FOUND, "Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
