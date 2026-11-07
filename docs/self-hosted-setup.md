# Quantheonix self-hosted server setup

The self-hosted stack runs the React dashboard, FastAPI, and PostgreSQL. Only
the dashboard is published to the host. Its Nginx server proxies `/api/` to the
private FastAPI service and disables buffering for streaming chat responses.

## Requirements

Install Git and Docker Desktop or Docker Engine with Docker Compose. Run all
commands below from the repository root in PowerShell.

Confirm Docker is available:

```powershell
docker version
docker compose version
```

## Configure the server

Create the ignored server environment file:

```powershell
Copy-Item .env.selfhosted.example .env.selfhosted
notepad .env.selfhosted
```

Set non-empty, private values for `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, and
`PROVIDER_KEY_ENCRYPTION_SECRET`. Generate independent JWT and provider-key
encryption secrets:

```powershell
py -c "import secrets; print(secrets.token_urlsafe(64))"
py -c "import secrets; print(secrets.token_urlsafe(64))"
```

Keep these dashboard defaults when the HTTPS reverse proxy runs on the Docker
host:

```env
DASHBOARD_BIND_ADDRESS=127.0.0.1
DASHBOARD_PORT=8080
```

Keep `PROVIDER_KEY_ENCRYPTION_SECRET` stable so stored assistant keys remain
decryptable. `GEMINI_API_KEY` is optional and acts only as a fallback for
explicitly grandfathered Gemini assistants. Newly registered users and newly
created assistants must save their own provider key in AI Settings.

Use a URL-safe PostgreSQL password because Compose places it in the backend
database URL. `CORS_ORIGINS=[]` is sufficient for the same-origin dashboard;
add only trusted origins for other browser applications.

## Validate and start

Render the final configuration before creating containers:

```powershell
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml config
```

Compose rejects blank required secrets. Start the stack and wait for all health
checks:

```powershell
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml up --build --wait
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml ps
```

The backend waits for PostgreSQL and runs `alembic upgrade head` before
Uvicorn starts. Verify the complete dashboard-to-API path:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/v1/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8080/
```

View startup and migration logs without displaying environment values:

```powershell
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml logs --tail 100 backend
```

## HTTPS reverse proxy

Terminate TLS at a reverse proxy on the server and forward the public hostname
to `http://127.0.0.1:8080`. An Nginx location can use:

```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
    proxy_read_timeout 3600s;
}
```

Expose only the HTTPS reverse proxy through the server firewall. PostgreSQL and
FastAPI have no published host ports in `compose.selfhosted.yaml`.

## Stop and restart

Stop containers while preserving PostgreSQL data:

```powershell
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml down
```

Restart them:

```powershell
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml up --wait
```

Do not add `--volumes` or `-v` to the server shutdown command.

## Data-preserving upgrades

The database volume remains explicitly named `quantheonix_postgres_data`.
Changing `.env.selfhosted` does not rewrite credentials in an already
initialized PostgreSQL volume. Keep its original database name, user, and
password unless you deliberately migrate them inside PostgreSQL.

Take and test a database or volume backup using the server's normal backup
process. Then update in place:

```powershell
git status --short
git pull --ff-only
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml pull postgres
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml up --build --wait
docker compose --env-file .env.selfhosted -f compose.selfhosted.yaml ps
Invoke-RestMethod http://127.0.0.1:8080/api/v1/health
```

Compose reuses `quantheonix_postgres_data`, and the backend applies pending
Alembic migrations before serving requests. Never run `down --volumes`,
`down -v`, or `docker volume rm quantheonix_postgres_data` during an upgrade.

For local Docker and native hot-reload commands, see
[run-modes.md](run-modes.md).
