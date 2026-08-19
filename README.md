# Task API

A small Task CRUD API built with Python 3.10+, FastAPI, and SQLite.

The service stores tasks in `tasks.db` inside this folder. The database file is created automatically when the app starts and is ignored by Git.

## Project Files

- `main.py`: FastAPI application and SQLite task logic.
- `requirements.txt`: Python dependencies.
- `COMMAND_LOG.md`: Stage-by-stage commands and actual checkpoint outputs.
- `README.md`: Setup and usage guide.
- `tasks.db`: Local SQLite database created on startup. This file is not committed.

## Requirements

- Python 3.10 or newer
- pip

## Setup

```powershell
cd "C:\Users\arfar\Downloads\Backend AI Engineer\task-api"
pip install -r requirements.txt
```

## Run

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Keep this terminal open while testing. Open a second terminal for curl commands.

If port `8000` is already in use, run on another port:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

## Swagger UI

After starting the server, open:

```txt
http://127.0.0.1:8000/docs
```

The OpenAPI schema is available at:

```txt
http://127.0.0.1:8000/openapi.json
```

## Database

SQLite is used through Python's standard `sqlite3` module.

Database file:

```txt
tasks.db
```

Table:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL
)
```

On startup, the app checks:

```sql
SELECT COUNT(*) FROM tasks
```

The default tasks are inserted only when the table is empty, so restarting the app does not duplicate seed data.

## Initial Seed Data

```json
[
  {"id": 1, "title": "Buy groceries", "done": false},
  {"id": 2, "title": "Read a chapter of a book", "done": true},
  {"id": 3, "title": "Review PRs", "done": false}
]
```

## Endpoints

### Service

```txt
GET /
GET /health
```

### Tasks

```txt
GET /tasks
GET /tasks/{id}
POST /tasks
PUT /tasks/{id}
DELETE /tasks/{id}
```

## Curl Examples

PowerShell requires doubled quotes inside JSON strings when passing JSON directly to `curl.exe`.

### Root

```powershell
curl.exe -sS -i http://127.0.0.1:8000/
```

### Health

```powershell
curl.exe -sS -i http://127.0.0.1:8000/health
```

### List Tasks

```powershell
curl.exe -sS -i http://127.0.0.1:8000/tasks
```

### Get Task

```powershell
curl.exe -sS -i http://127.0.0.1:8000/tasks/1
```

### Create Task

```powershell
curl.exe -sS -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{""title"":""Write tests""}'
```

### Update Task

```powershell
curl.exe -sS -i -X PUT http://127.0.0.1:8000/tasks/1 -H "Content-Type: application/json" -d '{""title"":""Buy milk"",""done"":true}'
```

### Delete Task

```powershell
curl.exe -sS -i -X DELETE http://127.0.0.1:8000/tasks/1
```

## Required Error Responses

Missing task:

```json
{"error": "Task not found"}
```

Missing or blank title:

```json
{"error": "Title is required and cannot be empty"}
```

Invalid JSON object body:

```json
{"error": "Request body must be a JSON object"}
```

Invalid `done` value:

```json
{"error": "Done must be a boolean"}
```

## Stage History

### Assignment 1

- Stage 0: hello server
- Stage 1: root and health endpoints
- Stage 2: read endpoints with 404
- Stage 3: create with validation
- Stage 4: full CRUD
- Stage 5: Swagger UI
- Stage 6: publish and docs

### Assignment 2

- Stage 0: create SQLite database
- Stage 1: database read endpoints
- Stage 2: insert into database
- Stage 3: update and delete with SQL
- Stage 4: explored SQLite
- Stage 5: database documentation
