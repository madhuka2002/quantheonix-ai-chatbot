# Running Quantheonix

All commands below are PowerShell commands run from the repository root. Real
environment files are ignored by Git. Never add API keys, JWT secrets, or
database passwords to a frontend environment file.

## 1. Full local Docker stack

Create the local Compose environment once. Provider keys can be configured per
assistant in AI Settings; `GEMINI_API_KEY` is only an optional fallback for
explicitly grandfathered Gemini assistants:

```powershell
Copy-Item .env.example .env
notepad .env
docker compose up --build --wait
```

The dashboard is available at <http://localhost:8080>. Its `/api/` requests are
proxied to FastAPI inside Compose, including streaming NDJSON responses. The API
is also published at `http://localhost:8000` for local debugging. PostgreSQL is
published at `localhost:5433` for native development tools.

The backend waits for PostgreSQL, applies `alembic upgrade head`, and only then
starts Uvicorn. Check the complete route through the dashboard proxy with:

```powershell
Invoke-RestMethod http://localhost:8080/api/v1/health
docker compose ps
```

Stop containers without removing data:

```powershell
docker compose down
```

### Carry settings forward from `backend/.env.docker`

`compose.yaml` now uses the root `.env`; it no longer loads
`backend/.env.docker`. Keep the old file as a private reference and manually
copy the values for `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_TEMPERATURE`,
`PROVIDER_KEY_ENCRYPTION_SECRET`, `JWT_SECRET_KEY`, token lifetimes,
`CORS_ORIGINS`, and rate limiting into the root `.env`. Copy the database name,
user, and password into the corresponding `POSTGRES_*` fields. Do not copy its
`DATABASE_URL`: Compose constructs the correct URL with host `postgres` and
container port `5432`.

An existing `quantheonix_dev_postgres_data` volume retains the credentials with
which it was initialized. Keep the matching `POSTGRES_*` values when upgrading;
changing the environment file does not rewrite users or passwords in an
existing PostgreSQL volume.

## 2. Native FastAPI and Vite with hot reload

Start only the development database. It listens on host port `5433`:

```powershell
docker compose up --wait postgres
```

In one PowerShell window, prepare and start FastAPI:

```powershell
Set-Location backend
Copy-Item .env.example .env
notepad .env
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend template uses `localhost:5433`. Make its database password match
the root `.env` used by PostgreSQL, set independent JWT and provider-key
encryption secrets, and optionally set the backend-only Gemini fallback.

In a second PowerShell window, start Vite:

```powershell
Set-Location frontend
Copy-Item .env.example .env
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

Open <http://127.0.0.1:5173>. `frontend/.env` contains only the public
`VITE_API_BASE_URL=http://127.0.0.1:8000`; Gemini, JWT, database, and other
server credentials stay in `backend/.env`.

## 3. Self-hosted server

Create the private server environment and fill every blank required secret:

```powershell
Copy-Item .env.selfhosted.example .env.selfhosted
notepad .env.selfhosted
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml config
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml up --build --wait
```

Compose refuses to render when `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, or
`PROVIDER_KEY_ENCRYPTION_SECRET` is blank. `GEMINI_API_KEY` is optional.
PostgreSQL and FastAPI have no host-published ports.
By default only the dashboard is published, on `127.0.0.1:8080`, for a reverse
proxy on the same server.

Point an HTTPS reverse proxy at `http://127.0.0.1:8080`. For Nginx, the proxy
location should disable response buffering so chat chunks are delivered as
they arrive:

```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
    proxy_read_timeout 3600s;
}
```

Terminate TLS at that proxy and expose only ports 80/443 in the server
firewall. Keep `DASHBOARD_BIND_ADDRESS=127.0.0.1` when the proxy runs on the
Docker host. Same-origin dashboard traffic needs no CORS entry; add only other
trusted browser origins to `CORS_ORIGINS`.

### Data-preserving upgrades

The self-hosted database volume remains explicitly named
`quantheonix_postgres_data`; the local volume remains
`quantheonix_dev_postgres_data`. Before an upgrade, take a tested database or
volume backup using your normal server backup process. Then update the source
and rebuild in place:

```powershell
git pull --ff-only
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml pull postgres
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml up --build --wait
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml ps
Invoke-RestMethod http://127.0.0.1:8080/api/v1/health
```

The named volume is reused and Alembic upgrades the existing schema before the
API starts. Do not use `down --volumes`, `down -v`, `docker volume rm`, or create
a replacement volume during an upgrade.
