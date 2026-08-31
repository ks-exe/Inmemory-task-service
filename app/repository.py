"""Repository layer for all PostgreSQL queries used by the Task API."""

from __future__ import annotations

from typing import Any

from app.database import get_connection

TaskRow = dict[str, Any]

SEED_TASKS: tuple[tuple[str, bool], ...] = (
    ("Complete Week 1 A3 Assignment", True),
    ("Containerize PostgreSQL with Docker", True),
    ("Write AI prompt and compare outputs", False),
)


def initialize_database() -> None:
    """Create the tasks table and seed it once when it is empty."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )
            cursor.execute("SELECT COUNT(*) AS count FROM tasks")
            result = cursor.fetchone()

            if result is not None and result["count"] == 0:
                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    SEED_TASKS,
                )


def list_tasks() -> list[TaskRow]:
    """Return all tasks sorted by insertion order."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks ORDER BY id ASC")
            return list(cursor.fetchall())


def get_task(task_id: int) -> TaskRow | None:
    """Return a task by primary key."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks WHERE id = %s",
                (task_id,),
            )
            return cursor.fetchone()


def create_task(title: str, done: bool) -> TaskRow:
    """Insert a task and return the created row."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                RETURNING id, title, done
                """,
                (title, done),
            )
            task = cursor.fetchone()

    if task is None:
        raise RuntimeError("Task insert did not return a row")

    return task


def update_task(task_id: int, title: str, done: bool) -> TaskRow | None:
    """Update a task and return the updated row, if it exists."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tasks
                SET title = %s, done = %s
                WHERE id = %s
                RETURNING id, title, done
                """,
                (title, done, task_id),
            )
            return cursor.fetchone()


def delete_task(task_id: int) -> bool:
    """Delete a task by primary key and report whether a row was removed."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id",
                (task_id,),
            )
            return cursor.fetchone() is not None


def check_database() -> None:
    """Run a lightweight database health check."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

