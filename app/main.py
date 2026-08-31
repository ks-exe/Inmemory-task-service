"""FastAPI application definition and route declarations."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Body, Depends, FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from app import database, repository
from app.auth import (
    AuthError,
    SupabaseConfigError,
    get_supabase_client,
    require_current_user,
    safe_user_payload,
)
from app.models import (
    AuthCredentials,
    DashboardResponse,
    ErrorResponse,
    HealthResponse,
    PublicInfoResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TokenResponse,
    UserProfileResponse,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    database.open_pool()
    repository.initialize_database()
    try:
        yield
    finally:
        database.close_pool()


app = FastAPI(
    title="FlyRank Week 2 A4 Auth Task API",
    description="Containerized FastAPI, PostgreSQL, and Supabase Auth task service.",
    version="2.0.0",
    lifespan=lifespan,
)


@app.exception_handler(AuthError)
def auth_error_handler(_: Request, exc: AuthError) -> JSONResponse:
    return _error(exc.status_code, exc.message)


def _error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


def _clean_title(title: str | None) -> str | None:
    if title is None:
        return None

    cleaned = title.strip()
    return cleaned or None


def _credentials_are_missing(payload: AuthCredentials | None) -> bool:
    if payload is None:
        return True
    return not payload.email or not payload.email.strip() or not payload.password or not payload.password.strip()


def _session_value(session: Any, field: str) -> Any:
    if session is None:
        return None
    return getattr(session, field, None)


@app.post(
    "/auth/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserProfileResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Sign up with Supabase Auth",
)
def signup(payload: AuthCredentials | None = Body(default=None)) -> dict[str, Any] | JSONResponse:
    if _credentials_are_missing(payload):
        return _error(status.HTTP_400_BAD_REQUEST, "Email and password are required")

    assert payload is not None

    try:
        response = get_supabase_client().auth.sign_up(
            {"email": payload.email.strip(), "password": payload.password}
        )
    except SupabaseConfigError as exc:
        return _error(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))
    except Exception as exc:
        return _error(status.HTTP_400_BAD_REQUEST, str(exc))

    user = getattr(response, "user", None)
    if user is None:
        return _error(status.HTTP_400_BAD_REQUEST, "Unable to create user")

    return safe_user_payload(user)


@app.post(
    "/auth/login",
    response_model=TokenResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Log in with Supabase Auth",
)
def login(payload: AuthCredentials | None = Body(default=None)) -> dict[str, Any] | JSONResponse:
    if _credentials_are_missing(payload):
        return _error(status.HTTP_400_BAD_REQUEST, "Email and password are required")

    assert payload is not None

    try:
        response = get_supabase_client().auth.sign_in_with_password(
            {"email": payload.email.strip(), "password": payload.password}
        )
    except SupabaseConfigError as exc:
        return _error(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))
    except Exception:
        return _error(status.HTTP_401_UNAUTHORIZED, "Invalid login credentials")

    session = getattr(response, "session", None)
    access_token = _session_value(session, "access_token")
    refresh_token = _session_value(session, "refresh_token")

    if not access_token:
        return _error(status.HTTP_401_UNAUTHORIZED, "Invalid login credentials")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@app.post(
    "/auth/logout",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Log out the current Supabase session",
)
def logout(_: Any = Depends(require_current_user)) -> Response:
    try:
        get_supabase_client().auth.sign_out()
    except SupabaseConfigError as exc:
        raise AuthError(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/public/info",
    response_model=PublicInfoResponse,
    summary="Read public information",
)
def public_info() -> dict[str, str]:
    return {"message": "Welcome stranger! This info is public."}


@app.get(
    "/protected/profile",
    response_model=UserProfileResponse,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Read the authenticated user profile",
)
def protected_profile(current_user: Any = Depends(require_current_user)) -> dict[str, Any]:
    return safe_user_payload(current_user)


@app.get(
    "/protected/dashboard",
    response_model=DashboardResponse,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Read a protected dashboard summary",
)
def protected_dashboard(current_user: Any = Depends(require_current_user)) -> dict[str, Any]:
    return {
        "status": "ok",
        "message": "Protected dashboard is available.",
        "user_id": getattr(current_user, "id", None),
    }


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
