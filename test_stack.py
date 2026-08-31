"""End-to-end verification for the containerized Task API stack.

Run after starting the stack:

    docker compose up --build
    python test_stack.py

The tests are also pytest-compatible:

    python -m pytest test_stack.py
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000").rstrip("/")

SEED_TASKS = [
    ("Complete Week 1 A3 Assignment", True),
    ("Containerize PostgreSQL with Docker", True),
    ("Write AI prompt and compare outputs", False),
]


@dataclass(frozen=True)
class APIResponse:
    status_code: int
    body: Any
    raw_body: bytes


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> APIResponse:
    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        url=f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=10) as response:
            raw_body = response.read()
            status_code = response.status
    except HTTPError as exc:
        raw_body = exc.read()
        status_code = exc.code
    except URLError as exc:
        raise AssertionError(
            f"Could not connect to {BASE_URL}. Start the stack with: docker compose up --build"
        ) from exc

    if raw_body:
        parsed_body = json.loads(raw_body.decode("utf-8"))
    else:
        parsed_body = None

    return APIResponse(status_code=status_code, body=parsed_body, raw_body=raw_body)


def assert_task_shape(task: dict[str, Any]) -> None:
    assert set(task.keys()) == {"id", "title", "done"}
    assert isinstance(task["id"], int)
    assert isinstance(task["title"], str)
    assert isinstance(task["done"], bool)


def get_seeded_tasks() -> list[dict[str, Any]]:
    response = request_json("GET", "/tasks")
    assert response.status_code == 200
    assert isinstance(response.body, list)
    assert len(response.body) == 3

    for task, (expected_title, expected_done) in zip(response.body, SEED_TASKS):
        assert_task_shape(task)
        assert task["title"] == expected_title
        assert task["done"] is expected_done

    return response.body


def test_health() -> None:
    response = request_json("GET", "/health")
    assert response.status_code == 200
    assert response.body == {"status": "ok", "db": "ok"}


def test_seeded_tasks() -> None:
    get_seeded_tasks()


def test_get_task_by_id() -> None:
    tasks = get_seeded_tasks()
    valid_task_id = tasks[0]["id"]

    found = request_json("GET", f"/tasks/{valid_task_id}")
    assert found.status_code == 200
    assert found.body == tasks[0]

    missing = request_json("GET", "/tasks/999")
    assert missing.status_code == 404
    assert missing.body == {"error": "Task not found"}


def test_create_validation_update_and_delete_flow() -> None:
    empty_title = request_json("POST", "/tasks", {"title": ""})
    assert empty_title.status_code == 400
    assert empty_title.body == {"error": "Title cannot be empty"}

    whitespace_title = request_json("POST", "/tasks", {"title": "   "})
    assert whitespace_title.status_code == 400
    assert whitespace_title.body == {"error": "Title cannot be empty"}

    created = request_json(
        "POST",
        "/tasks",
        {"title": "Verify automated stack test", "done": False},
    )
    assert created.status_code == 201
    assert_task_shape(created.body)
    assert created.body["title"] == "Verify automated stack test"
    assert created.body["done"] is False

    task_id = created.body["id"]

    updated = request_json(
        "PUT",
        f"/tasks/{task_id}",
        {"title": "Verify automated stack test is complete", "done": True},
    )
    assert updated.status_code == 200
    assert updated.body == {
        "id": task_id,
        "title": "Verify automated stack test is complete",
        "done": True,
    }

    missing_update = request_json(
        "PUT",
        "/tasks/999",
        {"title": "This task does not exist", "done": True},
    )
    assert missing_update.status_code == 404
    assert missing_update.body == {"error": "Task not found"}

    deleted = request_json("DELETE", f"/tasks/{task_id}")
    assert deleted.status_code == 204
    assert deleted.raw_body == b""
    assert deleted.body is None

    deleted_again = request_json("DELETE", f"/tasks/{task_id}")
    assert deleted_again.status_code == 404
    assert deleted_again.body == {"error": "Task not found"}

    missing_after_delete = request_json("GET", f"/tasks/{task_id}")
    assert missing_after_delete.status_code == 404
    assert missing_after_delete.body == {"error": "Task not found"}


def run_standalone() -> None:
    tests = [
        test_health,
        test_seeded_tasks,
        test_get_task_by_id,
        test_create_validation_update_and_delete_flow,
    ]

    for test in tests:
        test()
        print(f"PASS {test.__name__}")

    print("All stack tests passed.")


if __name__ == "__main__":
    run_standalone()
