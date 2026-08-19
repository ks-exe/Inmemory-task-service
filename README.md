# Task API

A small in-memory Task CRUD API built with Python 3.10+ and FastAPI.

The service stores tasks in a Python list only. It does not use a database, SQLite, or file-based persistence. Restarting the server resets the task list to the initial seed data.

## Repository

GitHub: https://github.com/ks-exe/Inmemory-task-service

## Project Files

- `main.py`: FastAPI application and in-memory task logic.
- `requirements.txt`: Python dependencies.
- `COMMAND_LOG.md`: Stage-by-stage commands and actual checkpoint outputs.
- `README.md`: Setup and usage guide.

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
{"error": "Task <id> not found"}
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

- Stage 0: hello server
- Stage 1: root and health endpoints
- Stage 2: read endpoints with 404
- Stage 3: create with validation
- Stage 4: full CRUD
- Stage 5: Swagger UI
- Stage 6: publish and docs
