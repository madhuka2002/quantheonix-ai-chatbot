# Quantheonix backend setup

This guide covers only the FastAPI backend: Python dependencies, PostgreSQL,
Alembic, JWT, backend environment variables, health checks, and Docker. For the
admin dashboard, see [systemfrontend-setup.md](systemfrontend-setup.md). For a
customer website, see the
[`@quantheonix/chatbot` guide](../packages/quantheonix-chatbot/README.md).

## Requirements

- Python 3.14
- PostgreSQL 17, or Docker Desktop with Compose
- PowerShell

## Start PostgreSQL for native backend development

From the repository root:

```powershell
Copy-Item .env.example .env
docker compose up --wait postgres
```

The development database is published at `127.0.0.1:5433`. Its data remains in
the named `quantheonix_dev_postgres_data` volume.

## Install Python dependencies

```powershell
Set-Location backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configure the backend

Create the ignored native environment file:

```powershell
Copy-Item .env.example .env
notepad .env
```

Important backend variables:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Async SQLAlchemy PostgreSQL URL; native development uses port `5433`. |
| `JWT_SECRET_KEY` | Signs access and refresh tokens. |
| `PROVIDER_KEY_ENCRYPTION_SECRET` | Encrypts assistant-owned Gemini/OpenAI/Anthropic keys. Keep it stable and separate from JWT. |
| `GEMINI_API_KEY` | Optional fallback for explicitly grandfathered Gemini assistants without an assistant-owned key. New assistants cannot inherit it. |
| `GEMINI_MODEL` / `GEMINI_TEMPERATURE` | Legacy Gemini fallback defaults. |
| `CORS_ORIGINS` | JSON list of trusted dashboard and authenticated browser API origins. Public widget sites are managed per assistant under **Allowed Domains**. |
| `RATE_LIMIT_*` | Authentication and chat rate-limit settings. |

Generate independent random values for JWT and provider-key encryption:

```powershell
py -c "import secrets; print(secrets.token_urlsafe(64))"
py -c "import secrets; print(secrets.token_urlsafe(64))"
```

Provider keys entered in the dashboard are encrypted before being stored.
They are write-only and are never returned by assistant or public widget APIs.
An OpenAI-only installation can leave `GEMINI_API_KEY` blank.

## Apply database migrations

From `backend` with the virtual environment active:

```powershell
alembic upgrade head
alembic current
```

The provider migrations keep existing assistants and conversations on Gemini,
preserve the intentional legacy fallback for existing Gemini assistants, and
disable operator-key inheritance for new assistants. Never edit an applied migration
or reset a production volume to deploy schema changes.

## Start FastAPI

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Verify API and database health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

When `DEBUG=true`, API documentation is available at
<http://127.0.0.1:8000/docs>.

## Run backend tests

Tests require a separate migrated PostgreSQL test database. Set
`DATABASE_URL` to that database, never to a database containing development or
production data, then run:

```powershell
alembic upgrade head
python -m pytest -q
```

CI uses an isolated PostgreSQL service and placeholder-only test credentials.

## Backend Docker image

The backend image remains in `backend/Dockerfile`:

```powershell
docker build -t quantheonix-backend ./backend
```

For a containerized backend connecting to host PostgreSQL, copy the Docker
template and edit its private values:

```powershell
Copy-Item backend/.env.docker.example backend/.env.docker
notepad backend/.env.docker
```

`host.docker.internal:5433` reaches the repository's development PostgreSQL
from Docker Desktop. Do not commit `backend/.env.docker`.

## Full backend through Compose

The root Compose stack waits for PostgreSQL, runs `alembic upgrade head`, and
starts Uvicorn:

```powershell
Set-Location ..
docker compose config
docker compose up --build --wait
docker compose ps
Invoke-RestMethod http://127.0.0.1:8080/api/v1/health
```

The `8080` health request verifies the dashboard's same-origin `/api/` proxy.
The direct development API is also available at `127.0.0.1:8000`.

Stop without removing the database volume:

```powershell
docker compose down
```

For production-like deployment, use
[self-hosted-setup.md](self-hosted-setup.md). Never use `down -v` or
`down --volumes` for data you need to keep.
