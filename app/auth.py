"""Supabase Auth client and reusable FastAPI authentication guard."""

from __future__ import annotations

import os
from datetime import date, datetime
from typing import Any

from dotenv import load_dotenv
from fastapi import Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

load_dotenv()

security = HTTPBearer(auto_error=False)


class AuthError(Exception):
    """Application auth error rendered as {"error": "..."} by main.py."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class SupabaseConfigError(RuntimeError):
    """Raised when Supabase credentials are not configured."""


def _supabase_settings() -> tuple[str, str]:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()

    if (
        not url
        or not key
        or url == "https://your-project.supabase.co"
        or key == "your-anon-key"
    ):
        raise SupabaseConfigError("Supabase credentials are not configured")

    return url, key


def _build_supabase_client() -> Client | None:
    try:
        url, key = _supabase_settings()
    except SupabaseConfigError:
        return None

    return create_client(url, key)


supabase: Client | None = _build_supabase_client()


def get_supabase_client() -> Client:
    """Return the process-wide Supabase client, creating it on first use."""
    global supabase

    if supabase is None:
        url, key = _supabase_settings()
        supabase = create_client(url, key)

    return supabase


def _json_value(value: Any) -> Any:
    if isinstance(value, datetime | date):
        return value.isoformat()
    return value


def safe_user_payload(user: Any) -> dict[str, Any]:
    """Return non-sensitive user fields suitable for API responses."""
    return {
        "id": _json_value(getattr(user, "id", None)),
        "email": _json_value(getattr(user, "email", None)),
        "created_at": _json_value(getattr(user, "created_at", None)),
    }


def require_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> Any:
    """Validate a Supabase access token and return the verified user."""
    if credentials is None or not credentials.credentials:
        raise AuthError(status.HTTP_401_UNAUTHORIZED, "Access token required")

    token = credentials.credentials.strip()
    if not token:
        raise AuthError(status.HTTP_401_UNAUTHORIZED, "Access token required")

    try:
        response = get_supabase_client().auth.get_user(token)
    except SupabaseConfigError as exc:
        raise AuthError(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc)) from exc
    except Exception as exc:
        raise AuthError(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token") from exc

    user = getattr(response, "user", None)
    if user is None:
        raise AuthError(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    return user
