# Quantheonix Self-Hosted Backend Setup

This guide explains how to deploy the Quantheonix AI Chatbot backend using Docker Compose and PostgreSQL.

The self-hosted deployment provides:

- FastAPI backend
- PostgreSQL database
- automatic Alembic migrations
- Gemini integration
- JWT authentication
- rate limiting
- persistent database storage
- health checks

---

# Architecture

```text
React Application
       |
       | HTTP / Streaming
       v
Quantheonix Backend
       |
       +----------------------+
       |                      |
       v                      v
PostgreSQL                Gemini API
```

Docker Compose manages the backend and PostgreSQL services.

---

# Requirements

Install:

- Git
- Docker
- Docker Compose

You also need:

- a Gemini API key
- a strong PostgreSQL password
- a strong JWT signing secret

Verify Docker:

```bash
docker --version
docker compose version
```

Make sure Docker Desktop or the Docker daemon is running before continuing.

---

# Step 1 — Clone Quantheonix

```bash
git clone https://github.com/madhuka2002/quantheonix-ai-chatbot.git
cd quantheonix-ai-chatbot
```

Verify the repository:

```bash
git status
```

A new clone should normally report a clean working tree.

---

# Step 2 — Create the Environment File

Copy:

```bash
cp .env.selfhosted.example .env.selfhosted
```

The resulting file:

```text
.env.selfhosted
```

contains the private deployment configuration.

Do not commit it.

---

# Step 3 — Configure PostgreSQL

Open:

```text
.env.selfhosted
```

Configure:

```env
POSTGRES_DB=quantheonix_chatbot
POSTGRES_USER=quantheonix_user
POSTGRES_PASSWORD=replace_with_a_strong_database_password
```

You may use another database name and username.

Example:

```env
POSTGRES_DB=quantheonix_chatbot_v1
POSTGRES_USER=quantheonix_user
POSTGRES_PASSWORD=your_private_password
```

The Compose configuration automatically uses these values for the backend database connection.

---

# Step 4 — Configure Gemini

Add your Gemini API key:

```env
GEMINI_API_KEY=replace_with_your_gemini_api_key
```

Configure the model:

```env
GEMINI_MODEL=gemini-flash-latest
GEMINI_TEMPERATURE=0.7
```

The Gemini API key stays on the server.

Never place it in the React application.

---

# Step 5 — Configure JWT

Generate a strong secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the generated value into:

```env
JWT_SECRET_KEY=YOUR_GENERATED_SECRET
```

Example configuration:

```env
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Never commit the real JWT secret.

---

# Step 6 — Configure CORS

For a local Vite application:

```env
CORS_ORIGINS=["http://localhost:5173"]
```

If both localhost forms are required:

```env
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

For production:

```env
CORS_ORIGINS=["https://your-domain.example"]
```

Multiple production applications can be configured:

```env
CORS_ORIGINS=["https://app.example.com","https://admin.example.com"]
```

The entries must be normal URL strings.

Do not use Markdown links.

---

# Step 7 — Validate Compose

Before starting containers:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  config >/dev/null && echo "Compose configuration OK"
```

Expected:

```text
Compose configuration OK
```

If this fails, correct the environment or YAML configuration before continuing.

---

# Step 8 — Start Quantheonix

Run:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  up -d --build
```

The first build can take several minutes.

Docker will:

1. download PostgreSQL if necessary
2. build the backend image
3. create the PostgreSQL volume
4. start PostgreSQL
5. wait for PostgreSQL health
6. start the backend
7. apply Alembic migrations
8. launch Uvicorn

---

# Step 9 — Check Containers

Run:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  ps
```

A successful installation should show both:

```text
quantheonix-postgres
quantheonix-backend
```

in healthy/running states.

---

# Step 10 — Check Backend Logs

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs backend
```

On a new database you should see Alembic migrations running before the backend starts.

The sequence should resemble:

```text
Applying database migrations...
...
Starting Quantheonix backend...
...
Application startup complete.
```

---

# Migration Safety

The self-hosted backend starts with:

```sh
set -e
```

before executing the migration command.

Conceptually:

```sh
set -e

alembic upgrade head

exec uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000
```

This is intentional.

If:

```bash
alembic upgrade head
```

fails, the backend process stops.

Quantheonix should not start normally against a database that failed its required migrations.

---

# Step 11 — Health Check

Run:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "Quantheonix AI Chatbot API",
  "version": "1.0.0",
  "database": "connected"
}
```

This confirms that:

- FastAPI is running
- the API is reachable
- PostgreSQL is reachable

---

# Step 12 — Connect the React Widget

Install:

```bash
npm install @quantheonix/chatbot
```

Import:

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";
```

Use:

```jsx
function App() {
  return (
    <QuantheonixChat
      apiUrl="http://localhost:8000"
    />
  );
}

export default App;
```

---

# Recommended Vite Configuration

Frontend `.env`:

```env
VITE_CHATBOT_API_URL=http://localhost:8000
```

Application:

```jsx
<QuantheonixChat
  apiUrl={
    import.meta.env.VITE_CHATBOT_API_URL
  }
/>
```

Restart Vite after changing its environment variables.

---

# Authentication Integration

If your application already has an access token:

```jsx
<QuantheonixChat
  apiUrl={
    import.meta.env.VITE_CHATBOT_API_URL
  }
  accessToken={
    localStorage.getItem("access_token")
  }
/>
```

For refresh-token support, provide `getAccessToken`.

Example:

```jsx
async function getAccessToken({
  forceRefresh = false,
} = {}) {
  if (!forceRefresh) {
    return localStorage.getItem(
      "access_token",
    );
  }

  const response = await fetch(
    `${import.meta.env.VITE_CHATBOT_API_URL}/api/v1/auth/refresh`,
    {
      method: "POST",
      credentials: "include",
    },
  );

  if (!response.ok) {
    return null;
  }

  const data = await response.json();

  localStorage.setItem(
    "access_token",
    data.access_token,
  );

  return data.access_token;
}
```

Then:

```jsx
<QuantheonixChat
  apiUrl={
    import.meta.env.VITE_CHATBOT_API_URL
  }
  getAccessToken={getAccessToken}
/>
```

---

# Database Persistence

PostgreSQL data is stored in a Docker volume.

Running:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  down
```

stops the services but preserves the database.

Restart:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  up -d
```

Your existing database should remain.

---

# Resetting the Database

> WARNING: The following operation deletes the PostgreSQL Docker volume and its stored data.

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  down -v
```

Then:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  up -d --build
```

PostgreSQL will initialize again using the current:

```env
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

values.

Alembic will then recreate the required schema.

---

# Important PostgreSQL Environment Behavior

PostgreSQL initialization variables are primarily used when the database volume is created.

For example, suppose you first start with:

```env
POSTGRES_PASSWORD=password_a
```

and PostgreSQL initializes its volume.

Changing the file later to:

```env
POSTGRES_PASSWORD=password_b
```

does not automatically rewrite the password stored in the already-initialized database.

This can result in:

```text
password authentication failed for user
```

For disposable development/test data, reset the volume:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  down -v
```

Do not use this approach on a production database containing data you need to preserve.

---

# View Logs

Backend:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs backend
```

PostgreSQL:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs postgres
```

Live backend logs:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs -f backend
```

---

# Stop Quantheonix

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  down
```

---

# Rebuild After Code Changes

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  up -d --build
```

---

# Updating from Git

Pull:

```bash
git pull
```

Then:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  up -d --build
```

Any new Alembic migrations are applied during backend startup.

---

# Production Checklist

Before deploying publicly:

- use a strong PostgreSQL password
- use a randomly generated JWT secret
- keep Gemini credentials private
- use HTTPS
- configure only trusted CORS origins
- keep rate limiting enabled
- do not commit `.env.selfhosted`
- back up PostgreSQL
- protect the host machine
- keep Docker updated
- review backend logs
- test the health endpoint
- verify authentication
- verify token refresh
- verify chat streaming

---

# Troubleshooting

See:

```text
docs/troubleshooting.md
```

for solutions to common deployment and configuration problems.