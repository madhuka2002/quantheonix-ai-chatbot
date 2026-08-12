# Quantheonix Troubleshooting Guide

This document covers common problems when developing, deploying, or integrating the Quantheonix AI Chatbot.

---

# 1. Docker Is Not Running

Symptoms may include errors connecting to the Docker daemon or Docker engine.

Check:

```bash
docker ps
```

If Docker is unavailable, start Docker Desktop or your Docker daemon and retry.

Then:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  up -d
```

---

# 2. `.env.selfhosted` Not Found

Example:

```text
couldn't find env file:
.../.env.selfhosted
```

Create it from the example:

```bash
cp .env.selfhosted.example .env.selfhosted
```

Confirm:

```bash
ls -la .env.selfhosted
```

Run Docker commands from the repository root:

```text
quantheonix-ai-chatbot/
```

not from:

```text
backend/
```

or another directory.

---

# 3. Validate Compose Configuration

Before debugging containers, validate Compose:

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

If this fails, fix the environment or Compose configuration first.

---

# 4. PostgreSQL Password Authentication Failed

Typical error:

```text
asyncpg.exceptions.InvalidPasswordError:
password authentication failed for user "quantheonix_user"
```

First verify:

```env
POSTGRES_DB=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
```

The backend database connection must use matching values.

Inspect the resolved configuration carefully:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  config
```

Warning: this output may expose secrets. Do not post it publicly.

---

# 5. Password Changed but PostgreSQL Still Rejects It

This commonly happens when PostgreSQL already initialized its Docker volume with an older password.

Changing:

```env
POSTGRES_PASSWORD=...
```

does not automatically change the password inside an existing initialized PostgreSQL database.

For disposable development/test data:

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

WARNING:

```bash
down -v
```

deletes the database volume.

Never do this on production data unless deletion is intentional and you have an appropriate backup.

---

# 6. Backend Container Starts but Database Is Unavailable

Check:

```bash
curl http://localhost:8000/api/v1/health
```

If the response reports a degraded or unavailable database state, inspect:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs backend
```

and:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs postgres
```

Common causes:

- incorrect PostgreSQL password
- wrong database name
- wrong PostgreSQL username
- existing database volume with old credentials
- PostgreSQL not ready
- database migration failure

---

# 7. Alembic Migration Failure

Backend startup automatically runs:

```bash
alembic upgrade head
```

before starting Uvicorn.

Check:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs backend
```

A successful fresh installation should show migrations followed by:

```text
Starting Quantheonix backend...
```

The self-hosted startup command uses:

```sh
set -e
```

so migration failure should stop backend startup.

This prevents the application from silently running against an invalid schema.

---

# 8. `alembic: command not found`

If you run:

```bash
alembic upgrade head
```

directly from the repository root and receive:

```text
alembic: command not found
```

your local Python environment either:

- is not active, or
- does not have the backend dependencies installed.

For the normal Docker self-hosted deployment, you do not need to execute Alembic manually.

Docker runs migrations inside the backend container.

For local backend development, create/activate the backend virtual environment and install:

```bash
pip install -r requirements.txt
```

before using Alembic directly.

---

# 9. CORS Error in Browser

Symptoms may include browser messages such as:

```text
blocked by CORS policy
```

Check:

```env
CORS_ORIGINS=["http://localhost:5173"]
```

If your frontend uses:

```text
http://127.0.0.1:5173
```

add it:

```env
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

For production:

```env
CORS_ORIGINS=["https://your-domain.example"]
```

Restart/rebuild the backend after changing backend environment configuration.

---

# 10. CORS Values Look Like Markdown Links

Incorrect:

```text
["[http://localhost:5173](http://localhost:5173)"]
```

Correct:

```env
CORS_ORIGINS=["http://localhost:5173"]
```

Verify what the application receives using the backend configuration tools available in your development environment.

The origin must be a normal URL string.

---

# 11. Widget Cannot Reach Backend

Verify the backend first:

```bash
curl http://localhost:8000/api/v1/health
```

Then check your frontend configuration:

```env
VITE_CHATBOT_API_URL=http://localhost:8000
```

And:

```jsx
<QuantheonixChat
  apiUrl={
    import.meta.env.VITE_CHATBOT_API_URL
  }
/>
```

Restart Vite after changing `.env`.

---

# 12. Wrong `apiUrl`

Correct:

```jsx
<QuantheonixChat
  apiUrl="http://localhost:8000"
/>
```

Do not point the widget directly to Gemini.

Incorrect concept:

```text
Browser → Gemini API
```

Correct architecture:

```text
Browser
   ↓
Quantheonix Backend
   ↓
Gemini API
```

---

# 13. HTTP 401 Unauthorized

A `401` generally means the access token is missing, expired, or invalid.

If using a fixed token:

```jsx
<QuantheonixChat
  apiUrl="http://localhost:8000"
  accessToken={accessToken}
/>
```

For refresh support, use:

```jsx
getAccessToken={getAccessToken}
```

The widget can request a new access token after receiving `401` and retry the request.

Check that the host application's refresh flow is working correctly.

---

# 14. Token Refresh Fails

Check that:

- refresh credentials exist
- the refresh endpoint is reachable
- the browser is sending the required credentials
- CORS is configured correctly
- the refresh token is not expired
- the callback returns the new access token

Example:

```jsx
const response = await fetch(
  `${apiUrl}/api/v1/auth/refresh`,
  {
    method: "POST",
    credentials: "include",
  },
);
```

If the callback returns `null`, the widget cannot retry authenticated chat successfully.

---

# 15. Gemini API Key Error

Check:

```env
GEMINI_API_KEY=...
```

The key must be configured on the backend.

Never configure it as a Vite/browser environment variable.

After changing backend credentials, restart the backend.

---

# 16. Gemini Model Not Available

If the configured model is unavailable for your API account, change:

```env
GEMINI_MODEL=...
```

to a model available to your Gemini API account.

The project configuration may use:

```env
GEMINI_MODEL=gemini-flash-latest
```

Always verify current model availability with your AI provider when model-related errors occur.

---

# 17. Gemini HTTP 429 / Resource Exhausted

A `429` generally indicates rate or quota exhaustion.

Symptoms may include:

```text
RESOURCE_EXHAUSTED
```

Possible causes:

- free-tier daily quota reached
- per-minute quota reached
- account/project quota restrictions

Wait for the relevant quota window to reset or review the quota associated with your Gemini project/account.

Do not repeatedly retry aggressively.

---

# 18. Streaming Does Not Work

Quantheonix chat streaming uses:

```text
/api/v1/chat/stream
```

and NDJSON:

```text
application/x-ndjson
```

Verify:

- backend is reachable
- authentication succeeds
- CORS is correct
- the request reaches `/api/v1/chat/stream`
- Gemini generation succeeds
- the browser is not terminating the request

Inspect backend logs:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs -f backend
```

---

# 19. Stop Button Does Not Work

The widget cancels active streaming using:

```text
AbortController
```

If the UI stops but the backend continues processing briefly, remember that aborting the browser request and cancelling provider-side generation are not necessarily identical operations.

Inspect the network request and backend logs if behavior is unexpected.

---

# 20. npm Package Cannot Be Found

Check:

```bash
npm view @quantheonix/chatbot
```

If the registry reports `404`, verify:

- the package has actually been published
- the scope is correct
- your npm registry is correct
- the package visibility is public if required

Check:

```bash
npm config get registry
```

Normally:

```text
https://registry.npmjs.org/
```

---

# 21. npm Authentication Error

Example:

```text
ENEEDAUTH
```

Check:

```bash
npm whoami
```

If necessary:

```bash
npm login --auth-type=web
```

Then:

```bash
npm whoami
```

---

# 22. npm Publishing Requires 2FA

npm may require two-factor authentication for package publishing.

Check:

```bash
npm profile get
```

If publishing requires write authentication, enable the appropriate npm 2FA configuration and authenticate during publishing.

---

# 23. npm Scope Not Found

For a scoped package:

```text
@quantheonix/chatbot
```

the `quantheonix` scope must exist and your npm account must have permission to publish into it.

If npm returns:

```text
Scope not found
```

verify the organization/scope configuration and account permissions.

---

# 24. Test a Local Package Tarball

Before publishing, build:

```bash
cd packages/quantheonix-chatbot

npm run lint
npm run build
npm pack
```

Then install the generated `.tgz` into another React project.

On Windows PowerShell, use a Windows path such as:

```powershell
npm install "E:\path\to\quantheonix-chatbot-0.1.0.tgz"
```

Do not mix Git Bash `/e/...` path syntax with PowerShell path handling.

---

# 25. Vite Production Build Warning About Large Chunks

You may see:

```text
Some chunks are larger than 500 kB after minification
```

This is a warning, not necessarily a failed build.

If:

```text
✓ built
```

appears, the build succeeded.

Future optimization can include:

- code splitting
- dynamic imports
- dependency optimization
- reducing bundled Markdown/highlighting code where practical

Treat optimization separately from functional release validation.

---

# 26. Port 8000 Already in Use

Check containers:

```bash
docker ps
```

If another service uses port `8000`, stop it or modify the host port mapping.

Do not run multiple conflicting backend instances on the same host port.

---

# 27. Port 5173 Already in Use

Vite may select another port if `5173` is unavailable.

If it changes to another port, add the actual frontend origin to:

```env
CORS_ORIGINS=[...]
```

Then restart the backend.

---

# 28. Orphan Docker Containers

Docker Compose may warn about orphan containers.

Inspect:

```bash
docker ps
```

If they belong to an obsolete version of the same Compose project, you can remove appropriate orphans using:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  down --remove-orphans
```

Be careful when other services intentionally share the same Compose project name.

---

# 29. Fresh Clone Behaves Differently from Development Copy

A fresh clone does not contain private ignored files such as:

```text
.env.selfhosted
backend/.env
backend/.env.docker
frontend/.env
```

That is expected.

Create private environment files from their examples.

Never solve this by committing secrets.

---

# 30. Git Says "Not a Git Repository"

Example:

```text
fatal: not a git repository
```

Check:

```bash
pwd
```

and:

```bash
ls -la
```

You must be inside the cloned repository containing:

```text
.git/
```

You can search nearby directories with:

```bash
find .. -maxdepth 3 -type d -name ".git" -print
```

Then enter the correct repository.

---

# 31. Verify Repository Before Committing

Run:

```bash
git status
git diff --check
```

`git diff --check` should produce no output when there are no whitespace errors.

Inspect changes:

```bash
git diff
```

Then commit only the intended files.

---

# 32. Health Check Says Healthy

A successful self-hosted backend should return something similar to:

```json
{
  "status": "healthy",
  "service": "Quantheonix AI Chatbot API",
  "version": "1.0.0",
  "database": "connected"
}
```

This is a strong indication that the API and database connection are operational.

For complete verification, also test:

- registration/authentication
- login
- token refresh
- chat
- streaming
- conversation continuation
- new conversation creation
- rate limiting

---

# Diagnostic Commands

Container status:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  ps
```

Backend logs:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs backend
```

PostgreSQL logs:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs postgres
```

Health:

```bash
curl http://localhost:8000/api/v1/health
```

Compose validation:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  config
```

Git state:

```bash
git status
git diff --check
```

---

# Security Reminder

Never post or commit:

```text
GEMINI_API_KEY
JWT_SECRET_KEY
POSTGRES_PASSWORD
DATABASE_URL containing credentials
refresh tokens
access tokens
```

If a real credential is accidentally exposed publicly, rotate it rather than merely deleting it from a later commit.