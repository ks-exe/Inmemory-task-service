import sqlite3
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

Task = dict[str, object]
BODY_INVALID_ERROR = {"error": "Request body must be a JSON object"}
DB_PATH = Path(__file__).with_name("tasks.db")
DONE_INVALID_ERROR = {"error": "Done must be a boolean"}
SEED_TASKS = [
    ("Buy groceries", 0),
    ("Read a chapter of a book", 1),
    ("Review PRs", 0),
]
TITLE_REQUIRED_ERROR = {"error": "Title is required and cannot be empty"}

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A SQLite-backed CRUD API for managing tasks.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database() -> None:
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL
            )
            """
        )

        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                SEED_TASKS,
            )

        conn.commit()
    finally:
        conn.close()


@app.on_event("startup")
def startup() -> None:
    setup_database()


def task_not_found_response() -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": "Task not found"},
    )


def row_to_task(row: sqlite3.Row) -> Task:
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


async def read_json_object(request: Request) -> dict[str, object] | None:
    try:
        payload = await request.json()
    except ValueError:
        return None

    if not isinstance(payload, dict):
        return None

    return payload


def parse_title(payload: dict[str, object] | None) -> str | None:
    if payload is None:
        return None

    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        return None

    return title.strip()


def parse_done(payload: dict[str, object], current_done: bool) -> bool | None:
    done = payload.get("done", current_done)
    if not isinstance(done, bool):
        return None

    return done


@app.get("/", tags=["Service"], summary="Show API metadata")
def root() -> dict[str, object]:
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", tags=["Service"], summary="Health check")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", tags=["Tasks"], summary="List tasks")
def list_tasks() -> list[Task]:
    conn = get_db()
    try:
        rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
        return [row_to_task(row) for row in rows]
    finally:
        conn.close()


@app.get("/tasks/{task_id}", tags=["Tasks"], summary="Get a task by ID")
def get_task(task_id: int):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return task_not_found_response()

    return row_to_task(row)


@app.post("/tasks", status_code=201, tags=["Tasks"], summary="Create a task")
async def create_task(request: Request):
    title = parse_title(await read_json_object(request))
    if title is None:
        return JSONResponse(status_code=400, content=TITLE_REQUIRED_ERROR)

    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 0),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
    finally:
        conn.close()

    return row_to_task(row)


@app.put("/tasks/{task_id}", tags=["Tasks"], summary="Update a task")
async def update_task(task_id: int, request: Request):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if row is None:
            return task_not_found_response()

        payload = await read_json_object(request)
        if payload is None:
            return JSONResponse(status_code=400, content=BODY_INVALID_ERROR)

        title = parse_title(payload)
        if title is None:
            return JSONResponse(status_code=400, content=TITLE_REQUIRED_ERROR)

        done = parse_done(payload, bool(row["done"]))
        if done is None:
            return JSONResponse(status_code=400, content=DONE_INVALID_ERROR)

        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (title, int(done), task_id),
        )
        conn.commit()

        updated = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return row_to_task(updated)
    finally:
        conn.close()


@app.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"], summary="Delete a task")
def delete_task(task_id: int):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return task_not_found_response()

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return Response(status_code=204)
    finally:
        conn.close()
