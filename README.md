# FlyRank Backend Track Week 2 Assignment A4

## Project Overview

This project extends the Week 1 containerized FastAPI + PostgreSQL task service with Week 2 Assignment A4, **Auth - Login & Protect**.

The API now supports:

- Supabase Auth sign up, login, and logout.
- Bearer token verification through the official Supabase Python SDK.
- Public and protected endpoints.
- Reusable FastAPI auth guard using `HTTPBearer`, so protected routes show the lock icon in Swagger UI.
- Existing PostgreSQL-backed task CRUD endpoints from A3.

## Stack

| Layer | Technology |
| --- | --- |
| API framework | FastAPI |
| Runtime | Python 3.11 |
| ASGI server | Uvicorn |
| Identity provider | Supabase Auth |
| Auth SDK | `supabase` Python SDK |
| Database | PostgreSQL 16 |
| PostgreSQL driver | psycopg 3 |
| Configuration | `.env` and environment variables |
| Container orchestration | Docker Compose |

## Project Structure

```text
.
+-- app/
|   +-- __init__.py
|   +-- auth.py
|   +-- database.py
|   +-- main.py
|   +-- models.py
|   +-- repository.py
+-- assets/
|   +-- screenshots/
|       +-- database-screenshot.png
|       +-- tasks-curl-output.png
+-- .env.example
+-- .gitignore
+-- Dockerfile
+-- compose.yaml
+-- README.md
+-- requirements.txt
+-- test_auth.py
+-- test_stack.py
```

## Configuration

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Fill in your Supabase project settings:

```env
DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks
DATABASE_POOL_MIN_SIZE=1
DATABASE_POOL_MAX_SIZE=10
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
PORT=8000
```

Supabase values:

- `SUPABASE_URL`: Supabase project URL from Project Settings.
- `SUPABASE_KEY`: Supabase anon public key from Project Settings > API.
- `.env` is ignored by Git and must not be committed.

For automated signup/login testing, disable email confirmation in Supabase Auth or use a pre-confirmed test account. In Supabase, this is under Authentication > Providers > Email.

## Run With Docker Compose

Start PostgreSQL and the API:

```bash
docker compose up --build -d
```

The Compose stack serves the API on:

```text
http://localhost:3000
```

Check health:

```bash
curl -i http://localhost:3000/health
```

Expected response:

```json
{"status":"ok","db":"ok"}
```

Stop the stack:

```bash
docker compose down
```

Reset PostgreSQL data:

```bash
docker compose down -v
```

## Run Locally Without Docker

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the API on the `.env` port, usually `8000`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

| Method | Path | Auth Required | Success | Errors | Description |
| --- | --- | --- | --- | --- | --- |
| GET | `/health` | No | `200 OK` | `500` | Checks PostgreSQL with `SELECT 1`. |
| GET | `/public/info` | No | `200 OK` | None | Public A4 endpoint. |
| POST | `/auth/signup` | No | `201 Created` | `400`, `500` | Creates a Supabase Auth user. |
| POST | `/auth/login` | No | `200 OK` | `400`, `401`, `500` | Logs in and returns bearer tokens. |
| POST | `/auth/logout` | Yes | `204 No Content` | `401`, `500` | Logs out the current Supabase session. |
| GET | `/protected/profile` | Yes | `200 OK` | `401`, `500` | Returns verified user metadata. |
| GET | `/protected/dashboard` | Yes | `200 OK` | `401`, `500` | Example protected dashboard route. |
| GET | `/tasks` | No | `200 OK` | `500` | Lists all tasks. |
| GET | `/tasks/{id}` | No | `200 OK` | `404` | Reads one task. |
| POST | `/tasks` | No | `201 Created` | `400` | Creates one task. |
| PUT | `/tasks/{id}` | No | `200 OK` | `400`, `404` | Updates one task. |
| DELETE | `/tasks/{id}` | No | `204 No Content` | `404` | Deletes one task. |

Standard error body:

```json
{"error":"Message here"}
```

## Auth curl Examples

### Public Endpoint

```bash
curl -i http://localhost:3000/public/info
```

Expected body:

```json
{"message":"Welcome stranger! This info is public."}
```

### Sign Up

```bash
curl -i -X POST http://localhost:3000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"student.a4.test@gmail.com","password":"strong-password-123"}'
```

Expected success body:

```json
{
  "id": "supabase-user-id",
  "email": "student.a4.test@gmail.com",
  "created_at": "2026-08-31T00:00:00Z"
}
```

Missing input example:

```bash
curl -i -X POST http://localhost:3000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected response:

```json
{"error":"Email and password are required"}
```

### Login

```bash
curl -i -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student.a4.test@gmail.com","password":"strong-password-123"}'
```

Expected body:

```json
{
  "access_token": "jwt-access-token",
  "token_type": "bearer",
  "refresh_token": "refresh-token"
}
```

Save the token:

```bash
TOKEN="paste-access-token-here"
```

PowerShell:

```powershell
$TOKEN = "paste-access-token-here"
```

### Protected Profile

```bash
curl -i http://localhost:3000/protected/profile \
  -H "Authorization: Bearer $TOKEN"
```

Expected body:

```json
{
  "id": "supabase-user-id",
  "email": "student.a4.test@gmail.com",
  "created_at": "2026-08-31T00:00:00Z"
}
```

Missing token:

```bash
curl -i http://localhost:3000/protected/profile
```

Expected response:

```json
{"error":"Access token required"}
```

Invalid token:

```bash
curl -i http://localhost:3000/protected/profile \
  -H "Authorization: Bearer invalid-token"
```

Expected response:

```json
{"error":"Invalid or expired token"}
```

### Protected Dashboard

```bash
curl -i http://localhost:3000/protected/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

Expected body:

```json
{
  "status": "ok",
  "message": "Protected dashboard is available.",
  "user_id": "supabase-user-id"
}
```

### Logout

```bash
curl -i -X POST http://localhost:3000/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

Expected status:

```http
HTTP/1.1 204 No Content
```

## Task curl Examples

```bash
curl -i http://localhost:3000/tasks
```

```bash
curl -i -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Review Supabase auth","done":false}'
```

```bash
curl -i -X PUT http://localhost:3000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Complete Week 2 A4 Assignment","done":true}'
```

```bash
curl -i -X DELETE http://localhost:3000/tasks/1
```

## Swagger UI Bearer Auth

Open:

```text
http://localhost:3000/docs
```

Use the `Authorize` button:

1. Log in with `/auth/login`.
2. Copy the returned `access_token`.
3. Click `Authorize`.
4. Enter only the token value if Swagger shows the HTTP Bearer field.
5. Run `/protected/profile` or `/protected/dashboard`.

The protected routes use one reusable FastAPI dependency based on `HTTPBearer`, so Swagger displays them with the lock icon.

## Automated Tests

Run the Week 1 stack tests:

```bash
python test_stack.py
```

Run the Week 2 auth tests after configuring Supabase credentials:

```bash
python test_auth.py
```

Expected auth output:

```text
PASS test_public_info
PASS test_signup_missing_input_validation
PASS test_signup_login_profile_and_logout_flow
All auth tests passed.
```

Pytest is also supported:

```bash
python -m pytest test_auth.py
```

## Submission Screenshots

### PostgreSQL Tasks Table

![PostgreSQL tasks table screenshot](assets/screenshots/database-screenshot.png)

### `curl.exe -i http://localhost:3000/tasks`

![curl tasks endpoint output](assets/screenshots/tasks-curl-output.png)
