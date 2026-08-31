# FlyRank Internship Backend Track Assignment A3

## Project Overview

This project implements Assignment A3, **Containerize your stack**, as a production-ready FastAPI service backed by PostgreSQL. The API exposes CRUD endpoints for a simple `tasks` table, automatically initializes the database schema on startup, and seeds three starter tasks when the table is empty.

The full stack runs with Docker Compose:

- `api`: FastAPI application served by Uvicorn on port `3000`
- `db`: PostgreSQL 16 with a persistent Docker volume

## Stack

| Layer | Technology |
| --- | --- |
| API framework | FastAPI |
| Runtime | Python 3.11 |
| ASGI server | Uvicorn |
| Database | PostgreSQL 16 |
| PostgreSQL driver | psycopg 3 |
| Configuration | Environment variables and python-dotenv |
| Container orchestration | Docker Compose |

## Project Structure

```text
.
+-- app/
|   +-- __init__.py
|   +-- database.py
|   +-- main.py
|   +-- models.py
|   +-- repository.py
+-- .env.example
+-- .gitignore
+-- Dockerfile
+-- compose.yaml
+-- README.md
+-- requirements.txt
+-- test_stack.py
```

## One-Command Setup

Start the API and PostgreSQL:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:3000
```

FastAPI documentation:

```text
http://localhost:3000/docs
```

Health check:

```bash
curl -i http://localhost:3000/health
```

Expected response:

```http
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok","db":"ok"}
```

## Configuration

The application reads PostgreSQL connection settings from `DATABASE_URL`.

Local example:

```env
DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks
DATABASE_POOL_MIN_SIZE=1
DATABASE_POOL_MAX_SIZE=10
```

Docker Compose injects this container-to-container value into the API service:

```env
DATABASE_URL=postgresql://postgres:dev@db:5432/tasks
```

## Database Initialization

On startup, the API:

1. Opens a psycopg connection pool.
2. Creates the `tasks` table if it does not exist.
3. Runs `SELECT COUNT(*) FROM tasks`.
4. Seeds exactly three starter tasks only when the table is empty.

Schema:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);
```

Seed data:

| Title | Done |
| --- | --- |
| Complete Week 1 A3 Assignment | true |
| Containerize PostgreSQL with Docker | true |
| Write AI prompt and compare outputs | false |

## Endpoint Table

| Method | Endpoint | Success Status | Error Status | Description |
| --- | --- | --- | --- | --- |
| GET | `/health` | `200 OK` | `500 Internal Server Error` if DB is unavailable | Runs `SELECT 1` against PostgreSQL. |
| GET | `/tasks` | `200 OK` | `500 Internal Server Error` if DB is unavailable | Returns all tasks ordered by `id`. |
| GET | `/tasks/{id}` | `200 OK` | `404 Not Found` | Returns one task by ID. |
| POST | `/tasks` | `201 Created` | `400 Bad Request` | Creates a task. Rejects missing, empty, or whitespace-only titles. |
| PUT | `/tasks/{id}` | `200 OK` | `400 Bad Request`, `404 Not Found` | Updates both `title` and `done`. |
| DELETE | `/tasks/{id}` | `204 No Content` | `404 Not Found` | Deletes a task and returns an empty body. |

Error response format:

```json
{"error":"Task not found"}
```

Validation error for empty titles:

```json
{"error":"Title cannot be empty"}
```

## curl Examples

### Health

```bash
curl -i http://localhost:3000/health
```

### List Tasks

```bash
curl -i http://localhost:3000/tasks
```

### Get Task By ID

```bash
curl -i http://localhost:3000/tasks/1
```

### Get Missing Task

```bash
curl -i http://localhost:3000/tasks/999
```

Expected body:

```json
{"error":"Task not found"}
```

### Create Task

```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Review Dockerized API","done":false}'
```

### Create Task With Default `done`

```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Document local setup"}'
```

### Reject Empty Title

```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"   "}'
```

Expected body:

```json
{"error":"Title cannot be empty"}
```

### Update Task

```bash
curl -i -X PUT http://localhost:3000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Complete Week 1 A3 Assignment","done":true}'
```

### Reject Update With Missing `done`

```bash
curl -i -X PUT http://localhost:3000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Missing done should fail"}'
```

Expected body:

```json
{"error":"Done field is required"}
```

### Delete Task

```bash
curl -i -X DELETE http://localhost:3000/tasks/1
```

Expected status:

```http
HTTP/1.1 204 No Content
```

## Automated Stack Verification

Start with a clean database volume for deterministic seed checks:

```bash
docker compose down -v
docker compose up --build
```

In a second terminal, run:

```bash
python test_stack.py
```

Expected output:

```text
PASS test_health
PASS test_seeded_tasks
PASS test_get_task_by_id
PASS test_create_validation_update_and_delete_flow
All stack tests passed.
```

The test script is also compatible with pytest:

```bash
python -m pytest test_stack.py
```

## Persistence Verification

Create a task:

```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Persistence check","done":false}'
```

Restart the containers without deleting the volume:

```bash
docker compose down
docker compose up --build
```

List tasks again:

```bash
curl -i http://localhost:3000/tasks
```

The `"Persistence check"` task should still be present because PostgreSQL data is stored in the named Docker volume `taskdata`.

To reset the database completely:

```bash
docker compose down -v
```

## Database Screenshot Instructions

To capture the required database screenshot, run:

```bash
docker compose exec db psql -U postgres -d tasks -c "SELECT id, title, done FROM tasks ORDER BY id;"
```

Take a screenshot showing:

- The terminal command.
- The `tasks` table rows.
- At least the three seeded assignment tasks.

For a clean screenshot with only seeded rows, reset the volume first:

```bash
docker compose down -v
docker compose up --build
docker compose exec db psql -U postgres -d tasks -c "SELECT id, title, done FROM tasks ORDER BY id;"
```

## Submission Screenshots

### PostgreSQL Tasks Table

![PostgreSQL tasks table screenshot](assets/screenshots/database-screenshot.png)

### `curl.exe -i http://localhost:3000/tasks`

![curl tasks endpoint output](assets/screenshots/tasks-curl-output.png)

## Stop The Stack

Stop containers while keeping database data:

```bash
docker compose down
```

Stop containers and remove persisted PostgreSQL data:

```bash
docker compose down -v
```
