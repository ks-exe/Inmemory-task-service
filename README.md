# FlyRank Week 2 Assignment A4: Auth - Login & Protect

## Project Overview

This repository contains a containerized FastAPI backend for the FlyRank Backend Track. Week 1 introduced a PostgreSQL-backed task API; Week 2 extends it with Supabase Auth as the external identity provider.

The application runs as a two-service Docker Compose stack:

- `api`: FastAPI application served by Uvicorn.
- `db`: PostgreSQL 16 with a persistent Docker volume.

Authentication is handled by Supabase Auth through the official `supabase` Python SDK. Public routes are available without credentials, while protected routes use a reusable FastAPI `HTTPBearer` dependency that validates the JWT access token with Supabase before allowing access.

## Architecture

```text
Client / Swagger UI / curl
        |
        | HTTP + Bearer JWT
        v
FastAPI API container
        |
        | psycopg pool
        v
PostgreSQL container

FastAPI API container
        |
        | Supabase Python SDK
        v
Supabase Auth Identity Provider
```

Important implementation files:

```text
app/main.py          FastAPI app, auth routes, public/protected routes, task routes
app/auth.py          Supabase client and reusable Bearer-token guard
app/database.py      PostgreSQL connection pool
app/repository.py    Raw SQL repository layer
app/models.py        Pydantic request/response models
test_auth.py         End-to-end auth verification script
```

## Environment Setup

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Fill in your local `.env` with real Supabase values:

```env
DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks
DATABASE_POOL_MIN_SIZE=1
DATABASE_POOL_MAX_SIZE=10
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
PORT=8000
```

Notes:

- `.env` is git-ignored and must never be committed.
- `SUPABASE_URL` is your Supabase project URL.
- `SUPABASE_KEY` is your Supabase anon public key.
- For automated signup/login tests, enable Email signups in Supabase and disable Confirm email:

```text
Supabase Dashboard > Authentication > Sign In / Providers > Email
```

Required settings:

```text
Enable email provider: ON
Allow new users to sign up: ON
Confirm email: OFF
```

## Running The Stack

Start the full stack:

```powershell
docker compose up --build -d
```

Check containers:

```powershell
docker compose ps
```

Health check:

```powershell
curl.exe -i http://localhost:3000/health
```

Run the A4 auth test suite:

```powershell
python test_auth.py
```

Expected output:

```text
PASS test_public_info
PASS test_signup_missing_input_validation
PASS test_signup_login_profile_and_logout_flow
All auth tests passed.
```

Stop the stack:

```powershell
docker compose down
```

## API Endpoint Reference

| Method | Endpoint | Auth Required | Expected Status Codes |
| --- | --- | --- | --- |
| `GET` | `/health` | No | `200` |
| `GET` | `/public/info` | No | `200` |
| `POST` | `/auth/signup` | No | `201`, `400` |
| `POST` | `/auth/login` | No | `200`, `400`, `401` |
| `POST` | `/auth/logout` | Yes | `204`, `401` |
| `GET` | `/protected/profile` | Yes | `200`, `401` |
| `GET` | `/protected/dashboard` | Yes | `200`, `401` |
| `GET` | `/tasks` | No | `200` |
| `GET` | `/tasks/{id}` | No | `200`, `404` |
| `POST` | `/tasks` | No | `201`, `400` |
| `PUT` | `/tasks/{id}` | No | `200`, `400`, `404` |
| `DELETE` | `/tasks/{id}` | No | `204`, `404` |

## cURL Examples

### Public Info

Request:

```powershell
curl.exe -i http://localhost:3000/public/info
```

Response:

```json
{"message":"Welcome stranger! This info is public."}
```

### Sign Up

Request:

```powershell
curl.exe -i -X POST http://localhost:3000/auth/signup `
  -H "Content-Type: application/json" `
  -d '{"email":"student@example.com","password":"strong-password-123"}'
```

Success response:

```json
{
  "id": "supabase-user-id",
  "email": "student@example.com",
  "created_at": "2026-09-04T17:00:00Z"
}
```

Missing input response:

```json
{"error":"Email and password are required"}
```

### Login

Request:

```powershell
curl.exe -i -X POST http://localhost:3000/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"student@example.com","password":"strong-password-123"}'
```

Success response:

```json
{
  "access_token": "jwt-access-token",
  "token_type": "bearer",
  "refresh_token": "refresh-token"
}
```

Save the token in PowerShell:

```powershell
$response = Invoke-RestMethod -Method Post `
  -Uri http://localhost:3000/auth/login `
  -ContentType "application/json" `
  -Body '{"email":"student@example.com","password":"strong-password-123"}'

$TOKEN = $response.access_token
```

### Protected Profile

Request with a valid token:

```powershell
curl.exe -i http://localhost:3000/protected/profile `
  -H "Authorization: Bearer $TOKEN"
```

Success response:

```json
{
  "id": "supabase-user-id",
  "email": "student@example.com",
  "created_at": "2026-09-04T17:00:00Z"
}
```

Request without a token:

```powershell
curl.exe -i http://localhost:3000/protected/profile
```

Unauthorized response:

```json
{"error":"Access token required"}
```

Request with an invalid or expired token:

```powershell
curl.exe -i http://localhost:3000/protected/profile `
  -H "Authorization: Bearer invalid-token"
```

Unauthorized response:

```json
{"error":"Invalid or expired token"}
```

### Protected Dashboard

Request:

```powershell
curl.exe -i http://localhost:3000/protected/dashboard `
  -H "Authorization: Bearer $TOKEN"
```

Response:

```json
{
  "status": "ok",
  "message": "Protected dashboard is available.",
  "user_id": "supabase-user-id"
}
```

### Logout

Request:

```powershell
curl.exe -i -X POST http://localhost:3000/auth/logout `
  -H "Authorization: Bearer $TOKEN"
```

Expected response:

```http
HTTP/1.1 204 No Content
```

## Swagger UI Auth Walkthrough

Open Swagger UI:

```text
http://localhost:3000/docs
```

Steps:

1. Run `POST /auth/login` with a valid email and password.
2. Copy the `access_token` value from the response.
3. Click the green `Authorize` button at the top of Swagger UI.
4. Paste the access token into the HTTP Bearer field.
5. Click `Authorize`, then close the modal.
6. Run `GET /protected/profile`.
7. A valid token returns `200 OK`; a missing, tampered, or expired token returns `401 Unauthorized`.

The lock icon appears on protected routes because the app uses FastAPI's `HTTPBearer` dependency centrally in `app/auth.py`.

## Verification Proof

### Login Returns Access Token

![Login response returning access token](assets/login_token.png)

### Protected Profile Returns 200 OK With Bearer Token

![Protected profile 200 OK](assets/profile_200.png)

### Protected Profile Returns 401 Unauthorized Without Valid Token

![Protected profile 401 Unauthorized](assets/profile_401.png)

### Automated Auth Tests Passing

![Auth tests passing](assets/tests_passing.png)

## Security Notes

- `.env` is ignored by Git and is not part of the repository.
- Supabase credentials are read from environment variables.
- No Supabase keys or JWT access tokens are hardcoded in application code.
- SQL operations remain isolated in the repository layer and use psycopg parameterized queries.

