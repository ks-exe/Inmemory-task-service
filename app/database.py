"""Database connection pool management.

This module owns connection lifecycle only. SQL and database operations live in
app.repository to keep the persistence layer isolated.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from dotenv import load_dotenv
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()

_pool: ConnectionPool | None = None


def _database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    return database_url


def open_pool() -> None:
    """Create the application-wide PostgreSQL connection pool."""
    global _pool

    if _pool is not None:
        return

    min_size = int(os.getenv("DATABASE_POOL_MIN_SIZE", "1"))
    max_size = int(os.getenv("DATABASE_POOL_MAX_SIZE", "10"))

    _pool = ConnectionPool(
        conninfo=_database_url(),
        min_size=min_size,
        max_size=max_size,
        kwargs={"row_factory": dict_row},
        open=False,
    )
    _pool.open()
    _pool.wait(timeout=10)


def close_pool() -> None:
    """Close the application-wide PostgreSQL connection pool."""
    global _pool

    if _pool is None:
        return

    _pool.close()
    _pool = None


@contextmanager
def get_connection() -> Iterator[Connection]:
    """Yield a pooled PostgreSQL connection."""
    if _pool is None:
        open_pool()

    if _pool is None:
        raise RuntimeError("Database connection pool is not initialized")

    with _pool.connection() as connection:
        yield connection
