"""End-to-end auth verification for FlyRank Week 2 A4.

Start the stack with Supabase credentials configured, then run:

    python test_auth.py

The tests are also pytest-compatible:

    python -m pytest test_auth.py
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def load_dotenv_file(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv_file()

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000").rstrip("/")
TEST_EMAIL = os.getenv("AUTH_TEST_EMAIL", f"flyrank-a4-{uuid.uuid4().hex}@example.com")
TEST_PASSWORD = os.getenv("AUTH_TEST_PASSWORD", "FlyRank-A4-test-password-123!")


@dataclass(frozen=True)
class APIResponse:
    status_code: int
    body: Any
    raw_body: bytes


def request_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
) -> APIResponse:
    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(
        url=f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=20) as response:
            raw_body = response.read()
            status_code = response.status
    except HTTPError as exc:
        raw_body = exc.read()
        status_code = exc.code
    except URLError as exc:
        raise AssertionError(
            f"Could not connect to {BASE_URL}. Start the service before running auth tests."
        ) from exc

    if raw_body:
        parsed_body = json.loads(raw_body.decode("utf-8"))
    else:
        parsed_body = None

    return APIResponse(status_code=status_code, body=parsed_body, raw_body=raw_body)


def assert_profile_shape(profile: dict[str, Any]) -> None:
    assert set(profile.keys()) == {"id", "email", "created_at"}
    assert profile["id"]
    assert profile["email"]
    assert "@" in profile["email"]


def test_public_info() -> None:
    response = request_json("GET", "/public/info")
    assert response.status_code == 200
    assert response.body == {"message": "Welcome stranger! This info is public."}


def test_signup_missing_input_validation() -> None:
    response = request_json("POST", "/auth/signup", {})
    assert response.status_code == 400
    assert response.body == {"error": "Email and password are required"}


def test_signup_login_profile_and_logout_flow() -> None:
    signup = request_json(
        "POST",
        "/auth/signup",
        {"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert signup.status_code == 201
    assert_profile_shape(signup.body)
    assert signup.body["email"].lower() == TEST_EMAIL.lower()

    time.sleep(1)

    login = request_json(
        "POST",
        "/auth/login",
        {"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert login.status_code == 200
    assert login.body["token_type"] == "bearer"
    assert login.body["access_token"]
    assert login.body["refresh_token"]

    access_token = login.body["access_token"]

    profile = request_json("GET", "/protected/profile", token=access_token)
    assert profile.status_code == 200
    assert_profile_shape(profile.body)
    assert profile.body["email"].lower() == TEST_EMAIL.lower()

    dashboard = request_json("GET", "/protected/dashboard", token=access_token)
    assert dashboard.status_code == 200
    assert dashboard.body["status"] == "ok"
    assert dashboard.body["user_id"] == profile.body["id"]

    tampered = request_json("GET", "/protected/profile", token=f"{access_token}.tampered")
    assert tampered.status_code == 401
    assert tampered.body == {"error": "Invalid or expired token"}

    missing = request_json("GET", "/protected/profile")
    assert missing.status_code == 401
    assert missing.body == {"error": "Access token required"}

    logout = request_json("POST", "/auth/logout", token=access_token)
    assert logout.status_code == 204
    assert logout.raw_body == b""
    assert logout.body is None


def run_standalone() -> None:
    tests = [
        test_public_info,
        test_signup_missing_input_validation,
        test_signup_login_profile_and_logout_flow,
    ]

    for test in tests:
        test()
        print(f"PASS {test.__name__}")

    print("All auth tests passed.")


if __name__ == "__main__":
    run_standalone()
