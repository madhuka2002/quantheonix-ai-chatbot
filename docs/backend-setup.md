# Quantheonix AI Chatbot — Backend Setup Guide

This guide explains how to install, configure, and run the backend required by the `@quantheonix/chatbot` React package.

The npm package provides the embeddable chatbot user interface. The backend provides the server-side functionality required for AI responses, authentication, conversation persistence, streaming, security, and database access.

---

# 1. Architecture

Quantheonix uses a client-server architecture.

```text
┌─────────────────────────────────────┐
│ User Website / React Application    │
│                                     │
│ @quantheonix/chatbot                │
└──────────────────┬──────────────────┘
                   │
                   │ HTTPS / REST
                   │ NDJSON Streaming
                   ▼
┌─────────────────────────────────────┐
│ Quantheonix Backend                 │
│ FastAPI                             │
│                                     │
│ • Authentication                    │
│ • JWT access/refresh tokens         │
│ • Conversations                     │
│ • Streaming responses               │
│ • Rate limiting                     │
│ • Gemini integration                │
└──────────────┬───────────────┬──────┘
               │               │
               │               │
               ▼               ▼
      ┌────────────────┐  ┌───────────────┐
      │ PostgreSQL     │  │ Gemini API    │
      │                │  │               │
      │ Users          │  │ AI generation │
      │ Conversations  │  │               │
      │ Messages       │  │               │
      └────────────────┘  └───────────────┘
```

The React application must **never directly communicate with Gemini using a private Gemini API key**.

Secrets remain on the backend.

---

# 2. What the Backend Provides

The Quantheonix backend is responsible for:

- User registration
- User login
- JWT authentication
- Access tokens
- Refresh tokens
- Token validation
- Conversation management
- Conversation persistence
- AI message generation
- Streaming AI responses
- PostgreSQL database access
- Gemini API communication
- Rate limiting
- CORS protection
- Error handling
- API health monitoring

The npm package communicates with this backend.

---

# 3. Requirements

Before running the backend, install the required software.

## Required

- Git
- Python
- PostgreSQL
- A Gemini API key

## Recommended

- Docker Desktop
- Docker Compose

For local Python development, Python 3.11 or newer is recommended.

The project may also be run through Docker.

---

# 4. Clone the Repository

Clone the Quantheonix repository:

```bash
git clone https://github.com/madhuka2002/quantheonix-ai-chatbot.git
```

Enter the project:

```bash
cd quantheonix-ai-chatbot
```

The repository contains multiple components.

Example structure:

```text
quantheonix-ai-chatbot/
│
├── backend/
│   ├── app/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── .env.docker.example
│
├── frontend/
│
├── packages/
│   └── quantheonix-chatbot/
│
├── docs/
│
└── compose.yaml
```

---

# 5. Backend Configuration

Enter the backend directory:

```bash
cd backend
```

The backend requires environment variables.

Never place real secrets directly inside source code.

Never commit the real `.env` file.

---

# 6. Create the Environment File

A safe configuration template is provided as:

```text
.env.example
```

Copy it to:

```text
.env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Git Bash / Linux / macOS

```bash
cp .env.example .env
```

Then edit:

```text
backend/.env
```

---

# 7. Environment Configuration

A typical development configuration looks similar to:

```env
APP_NAME=Quantheonix AI Chatbot API
APP_VERSION=0.1.0
DEBUG=true

API_V1_PREFIX=/api/v1

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-flash-latest
GEMINI_TEMPERATURE=0.7

DATABASE_URL=postgresql+asyncpg://quantheonix_user:your_password@localhost:5432/quantheonix_chatbot

JWT_SECRET_KEY=your_generated_jwt_secret
JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

RATE_LIMIT_ENABLED=true
RATE_LIMIT_LOGIN_REQUESTS=10
RATE_LIMIT_REGISTER_REQUESTS=5
RATE_LIMIT_REFRESH_REQUESTS=30
RATE_LIMIT_CHAT_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
```

Replace all placeholder values before running the application.

---

# 8. Gemini API Configuration

The backend requires a Gemini API key to generate AI responses.

Set:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The configured model can be specified using:

```env
GEMINI_MODEL=gemini-flash-latest
```

Temperature can be configured using:

```env
GEMINI_TEMPERATURE=0.7
```

## Important Security Rule

Never place the Gemini API key in:

```text
frontend/.env
```

or:

```text
VITE_GEMINI_API_KEY
```

or directly inside React/JavaScript code.

Anything included in browser JavaScript can potentially be inspected by users.

The correct architecture is:

```text
Browser
   │
   ▼
Quantheonix Backend
   │
   │ GEMINI_API_KEY
   ▼
Gemini API
```

---

# 9. JWT Configuration

Quantheonix uses JWT authentication.

You must generate your own secure JWT secret.

Do not reuse the example value from documentation.

Generate one with Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Example output:

```text
a_random_secure_value_generated_by_python
```

Copy the generated value into:

```env
JWT_SECRET_KEY=your_generated_value
```

Configure the algorithm:

```env
JWT_ALGORITHM=HS256
```

Access-token lifetime:

```env
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Refresh-token lifetime:

```env
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

# 10. PostgreSQL Setup

Quantheonix uses PostgreSQL for persistent application data.

The database stores information required by backend features such as users, conversations, and messages.

A typical database name is:

```text
quantheonix_chatbot
```

A typical database URL is:

```env
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@HOST:5432/quantheonix_chatbot
```

---

# 11. PostgreSQL Running Locally

If PostgreSQL runs directly on the same computer as the Python backend:

```env
DATABASE_URL=postgresql+asyncpg://quantheonix_user:your_password@localhost:5432/quantheonix_chatbot
```

The important parts are:

```text
postgresql+asyncpg://
        │
        ├── username
        ├── password
        ├── host
        ├── port
        └── database
```

Example:

```text
postgresql+asyncpg://quantheonix_user:password@localhost:5432/quantheonix_chatbot
```

---

# 12. Backend in Docker + PostgreSQL on Host

If the Quantheonix backend runs inside Docker but PostgreSQL runs directly on the host computer, `localhost` inside the container refers to the container itself.

Therefore, on Docker Desktop, use:

```env
DATABASE_URL=postgresql+asyncpg://quantheonix_user:your_password@host.docker.internal:5432/quantheonix_chatbot
```

Architecture:

```text
Docker Container
Quantheonix Backend
       │
       │ host.docker.internal
       ▼
Host Computer
PostgreSQL
```

---

# 13. PostgreSQL in Docker Compose

If PostgreSQL is also running as a Docker Compose service, use the PostgreSQL service name as the hostname.

For example, if the Compose service is named:

```yaml
services:
  postgres:
```

the backend database URL can use:

```env
DATABASE_URL=postgresql+asyncpg://quantheonix_user:your_password@postgres:5432/quantheonix_chatbot
```

Architecture:

```text
Docker Compose Network

┌─────────────────────┐
│ backend             │
│ FastAPI             │
└──────────┬──────────┘
           │
           │ postgres:5432
           ▼
┌─────────────────────┐
│ postgres            │
│ PostgreSQL          │
└─────────────────────┘
```

Docker Compose automatically provides service-name DNS inside its network.

---

# 14. Cloud PostgreSQL

Quantheonix can also use a managed PostgreSQL database.

In that case, replace `DATABASE_URL` with the connection information supplied by your database provider.

Example format:

```env
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@DATABASE_HOST:5432/DATABASE_NAME
```

Never commit cloud database credentials to Git.

---

# 15. CORS Configuration

CORS controls which browser origins are allowed to call the Quantheonix backend.

This is important because the npm chatbot runs inside another website.

For local Vite development:

```env
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

If the Docker frontend runs on port `8080`:

```env
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:8080","http://127.0.0.1:8080"]
```

---

# 16. Production CORS

Suppose the chatbot is installed on:

```text
https://example.com
```

Configure:

```env
CORS_ORIGINS=["https://example.com"]
```

If both versions are used:

```text
https://example.com
https://www.example.com
```

configure:

```env
CORS_ORIGINS=["https://example.com","https://www.example.com"]
```

Only trusted frontend origins should be added.

---

# 17. Do Not Use Wildcard CORS in Authenticated Production Systems

Avoid:

```env
CORS_ORIGINS=["*"]
```

for authenticated production applications.

Instead explicitly list trusted frontend origins.

Example:

```env
CORS_ORIGINS=["https://shop.example.com","https://admin.example.com"]
```

---

# 18. Python Development Setup

Enter the backend directory:

```bash
cd backend
```

Create a virtual environment.

### Windows

```bash
python -m venv .venv
```

Activate from Git Bash:

```bash
source .venv/Scripts/activate
```

Activate from PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# 19. Install Python Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

Verify Python:

```bash
python --version
```

Verify installed packages:

```bash
pip list
```

---

# 20. Validate the Backend

Before starting the server, compile the Python source:

```bash
python -m compileall app main.py
```

Then verify that the application can be imported:

```bash
python -c "import main; print('Backend OK')"
```

Expected:

```text
Backend OK
```

---

# 21. Run Backend Tests

Run:

```bash
pytest -v
```

A successful test run should complete without failed tests.

If pytest is not installed:

```bash
pip install pytest pytest-asyncio
```

Then run:

```bash
pytest -v
```

---

# 22. Start the Backend Locally

Start FastAPI using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

For development with automatic reload:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend should now be available at:

```text
http://localhost:8000
```

---

# 23. Swagger API Documentation

FastAPI provides interactive API documentation.

Open:

```text
http://localhost:8000/docs
```

The Swagger interface can be used to inspect and test backend endpoints.

---

# 24. API Versioning

The default API prefix is:

```env
API_V1_PREFIX=/api/v1
```

Therefore API endpoints use URLs similar to:

```text
/api/v1/...
```

The chatbot npm package currently communicates with the streaming chat endpoint:

```text
/api/v1/chat/stream
```

The complete URL during local development is therefore:

```text
http://localhost:8000/api/v1/chat/stream
```

---

# 25. Streaming

The npm chatbot uses streaming responses.

The backend returns NDJSON streaming events.

The client expects:

```text
application/x-ndjson
```

Typical stream events include:

```json
{"type":"start","conversation_id":"..."}
```

followed by events similar to:

```json
{"type":"chunk","text":"Hello"}
```

and finally:

```json
{"type":"done","conversation_id":"..."}
```

The npm package processes these events and progressively displays the AI response.

---

# 26. Authentication

Protected backend requests use:

```http
Authorization: Bearer ACCESS_TOKEN
```

The npm package supports an access token through:

```jsx
<QuantheonixChat
  apiUrl="http://localhost:8000"
  accessToken={accessToken}
/>
```

For applications that support token refresh, using `getAccessToken` is recommended.

Example:

```jsx
<QuantheonixChat
  apiUrl="http://localhost:8000"
  getAccessToken={async ({ forceRefresh }) => {
    if (forceRefresh) {
      return await refreshAccessToken();
    }

    return currentAccessToken;
  }}
/>
```

If a request receives HTTP `401`, the widget can request a refreshed token through this callback and retry the chat request.

---

# 27. Rate Limiting

Quantheonix includes application-level rate limiting.

Example configuration:

```env
RATE_LIMIT_ENABLED=true

RATE_LIMIT_LOGIN_REQUESTS=10
RATE_LIMIT_REGISTER_REQUESTS=5
RATE_LIMIT_REFRESH_REQUESTS=30
RATE_LIMIT_CHAT_REQUESTS=20

RATE_LIMIT_WINDOW_SECONDS=60
```

These limits help reduce abuse and excessive requests.

Production limits should be adjusted according to expected traffic and infrastructure capacity.

---

# 28. Docker Setup

The backend includes a Dockerfile.

From the backend directory:

```bash
docker build -t quantheonix-chatbot-backend .
```

Verify that the image exists:

```bash
docker images
```

---

# 29. Docker Environment File

For Docker, copy:

```text
.env.docker.example
```

to:

```text
.env.docker
```

Git Bash/Linux/macOS:

```bash
cp .env.docker.example .env.docker
```

PowerShell:

```powershell
Copy-Item .env.docker.example .env.docker
```

Then edit the real values.

Never commit:

```text
.env.docker
```

---

# 30. Run the Backend Container

From the backend directory:

```bash
docker run --rm \
  -p 8000:8000 \
  --env-file .env.docker \
  quantheonix-chatbot-backend
```

PowerShell can also run the command on one line:

```powershell
docker run --rm -p 8000:8000 --env-file .env.docker quantheonix-chatbot-backend
```

The backend should then be accessible at:

```text
http://localhost:8000
```

---

# 31. Docker Compose

The repository also contains:

```text
compose.yaml
```

From the repository root, start the configured services using:

```bash
docker compose up -d --build
```

Check their status:

```bash
docker compose ps
```

View backend logs:

```bash
docker compose logs backend
```

Follow backend logs:

```bash
docker compose logs -f backend
```

View frontend logs:

```bash
docker compose logs frontend
```

---

# 32. Stop Docker Compose

Stop the services:

```bash
docker compose down
```

Start them again:

```bash
docker compose up -d
```

Rebuild after source changes:

```bash
docker compose up -d --build
```

---

# 33. Connect the React npm Package

Install the frontend package:

```bash
npm install @quantheonix/chatbot
```

Import it:

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";
```

Use it:

```jsx
function App() {
  return (
    <QuantheonixChat
      apiUrl="http://localhost:8000"
      title="AI Assistant"
      welcomeMessage="Hello! How can I help you?"
      placeholder="Type your message..."
      initiallyOpen={false}
      position="bottom-right"
    />
  );
}

export default App;
```

---

# 34. Frontend Environment Variable

Instead of hardcoding the backend URL, a Vite application can use:

```env
VITE_CHATBOT_API_URL=http://localhost:8000
```

Then:

```jsx
<QuantheonixChat
  apiUrl={
    import.meta.env.VITE_CHATBOT_API_URL
  }
/>
```

In production:

```env
VITE_CHATBOT_API_URL=https://api.example.com
```

The backend URL is not a secret and may be visible in browser code.

---

# 35. Supported Widget Positions

The current npm package supports:

```jsx
position="bottom-right"
```

and:

```jsx
position="bottom-left"
```

The default is:

```text
bottom-right
```

---

# 36. Example Development Architecture

A common local development configuration is:

```text
React/Vite
http://localhost:5173
        │
        │
        ▼
Quantheonix Backend
http://localhost:8000
        │
        ├──────────────► Gemini API
        │
        ▼
PostgreSQL
localhost:5432
```

Backend CORS:

```env
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

Frontend:

```env
VITE_CHATBOT_API_URL=http://localhost:8000
```

---

# 37. Example Production Architecture

A production deployment may look like:

```text
https://example.com
        │
        │ @quantheonix/chatbot
        ▼
https://api.example.com
        │
        ├──────────────► Gemini API
        │
        ▼
Managed PostgreSQL
```

Backend:

```env
DEBUG=false

CORS_ORIGINS=["https://example.com"]

DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@DATABASE_HOST:5432/quantheonix_chatbot

GEMINI_API_KEY=production_api_key

JWT_SECRET_KEY=production_generated_secret
```

Frontend:

```env
VITE_CHATBOT_API_URL=https://api.example.com
```

---

# 38. Production Security Checklist

Before deploying publicly, verify:

- `DEBUG=false`
- Gemini API key exists only on the backend
- JWT secret is randomly generated
- Database credentials are not committed
- `.env` is ignored by Git
- `.env.docker` is ignored by Git
- Only `.env.example` files are committed
- Production HTTPS is enabled
- CORS contains only trusted origins
- PostgreSQL is protected from unnecessary public access
- Rate limiting is enabled
- Strong database passwords are used
- Access tokens have limited lifetime
- Refresh-token behavior has been tested
- Backend logs do not expose secrets

---

# 39. Verify Secrets Are Not Tracked

From the repository root:

```bash
git ls-files | grep -E '(^|/)\.env($|\.docker)'
```

Ideally, real environment files should not appear.

Check:

```bash
git check-ignore backend/.env
git check-ignore backend/.env.docker
```

Expected:

```text
backend/.env
backend/.env.docker
```

The safe templates should remain trackable:

```text
backend/.env.example
backend/.env.docker.example
```

---

# 40. Health Check

After starting the backend, verify that the configured health endpoint responds successfully.

You can also inspect the API through:

```text
http://localhost:8000/docs
```

If the health endpoint or exact route differs in a future version, use the route documented by the current backend API.

---

# 41. Common Problem — Database Connection Failed

If the backend cannot connect to PostgreSQL, verify:

1. PostgreSQL is running.
2. The database exists.
3. Username is correct.
4. Password is correct.
5. Port is correct.
6. Database name is correct.
7. The hostname matches the deployment environment.

For local Python:

```text
localhost
```

For Docker backend connecting to host PostgreSQL:

```text
host.docker.internal
```

For Docker Compose PostgreSQL:

```text
postgres
```

assuming the service is named `postgres`.

---

# 42. Common Problem — CORS Error

If the browser reports a CORS error, check the exact frontend origin.

For example, if the frontend runs at:

```text
http://localhost:5173
```

the backend should contain:

```env
CORS_ORIGINS=["http://localhost:5173"]
```

Origins include the:

- protocol
- hostname
- port

Therefore:

```text
http://localhost:5173
```

and:

```text
http://localhost:8080
```

are different origins.

Restart the backend after changing environment variables.

---

# 43. Common Problem — 401 Unauthorized

A `401` usually indicates that authentication is required or that the access token is invalid or expired.

Check:

- The user is logged in.
- An access token is being supplied.
- The token has not expired.
- The frontend refresh-token logic works.
- `getAccessToken` returns the new token when `forceRefresh` is `true`.

---

# 44. Common Problem — Gemini Request Fails

Verify:

```env
GEMINI_API_KEY=...
```

and:

```env
GEMINI_MODEL=gemini-flash-latest
```

Also check:

- API-key validity
- model availability
- provider quota
- request limits
- backend logs

Do not move the Gemini API key into the frontend to work around a backend configuration problem.

---

# 45. Common Problem — Docker Cannot Reach PostgreSQL

If the backend is inside Docker while PostgreSQL is installed on the host computer, do not normally use:

```text
localhost
```

inside the container.

Use:

```text
host.docker.internal
```

Example:

```env
DATABASE_URL=postgresql+asyncpg://quantheonix_user:PASSWORD@host.docker.internal:5432/quantheonix_chatbot
```

---

# 46. Common Problem — Docker Container Does Not Start

Check:

```bash
docker compose ps
```

Then:

```bash
docker compose logs backend
```

or:

```bash
docker logs CONTAINER_NAME
```

Common causes include:

- invalid `DATABASE_URL`
- missing `GEMINI_API_KEY`
- missing `JWT_SECRET_KEY`
- invalid environment-variable formatting
- PostgreSQL unavailable
- port `8000` already in use

---

# 47. Environment File Formatting

Environment variables should use:

```env
NAME=value
```

Do not accidentally write:

```env
DATABASE_URL=DATABASE_URL=postgresql+asyncpg://...
```

Correct:

```env
DATABASE_URL=postgresql+asyncpg://...
```

For CORS, use valid JSON-style list syntax if required by the backend settings:

```env
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

Do not copy Markdown-formatted links into `.env`.

Incorrect:

```env
CORS_ORIGINS=["[http://localhost:5173](http://localhost:5173)"]
```

Correct:

```env
CORS_ORIGINS=["http://localhost:5173"]
```

---

# 48. Do Not Commit Secrets

Never commit files containing:

```text
GEMINI_API_KEY
JWT_SECRET_KEY
database passwords
production credentials
```

The repository should contain templates such as:

```text
.env.example
.env.docker.example
```

but not:

```text
.env
.env.docker
```

---

# 49. Backend URL vs Gemini URL

The npm package's `apiUrl` must point to the **Quantheonix backend**.

Correct:

```jsx
<QuantheonixChat
  apiUrl="https://api.example.com"
/>
```

Do not give the npm widget a Gemini API URL or Gemini API key.

The widget automatically calls the required Quantheonix backend routes.

---

# 50. Deployment Responsibility

When using the self-hosted version of Quantheonix, the person deploying the backend is responsible for:

- hosting the FastAPI backend
- configuring PostgreSQL
- obtaining a Gemini API key
- generating a JWT secret
- configuring CORS
- protecting environment variables
- configuring HTTPS
- maintaining the server
- monitoring usage
- managing backups
- updating the application

The npm package itself does not host these services.

---

# 51. Recommended Deployment Model

For development:

```text
Frontend:
http://localhost:5173

Backend:
http://localhost:8000

PostgreSQL:
localhost:5432
```

For production:

```text
Frontend:
https://example.com

Backend:
https://api.example.com

Database:
Managed/private PostgreSQL
```

Always use HTTPS for production traffic.

---

# 52. Quick Start Summary

For experienced developers, the basic setup is:

```bash
git clone https://github.com/madhuka2002/quantheonix-ai-chatbot.git

cd quantheonix-ai-chatbot/backend

python -m venv .venv
source .venv/Scripts/activate

pip install -r requirements.txt

cp .env.example .env
```

Configure:

```env
GEMINI_API_KEY=...
DATABASE_URL=...
JWT_SECRET_KEY=...
CORS_ORIGINS=["http://localhost:5173"]
```

Start:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then in the React application:

```bash
npm install @quantheonix/chatbot
```

Use:

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

function App() {
  return (
    <QuantheonixChat
      apiUrl="http://localhost:8000"
      position="bottom-right"
    />
  );
}

export default App;
```

---

# 53. Security Boundary

Remember the most important architecture rule:

```text
PUBLIC / BROWSER
────────────────────────────────

React Application
@quantheonix/chatbot
Backend URL
Access token where applicable

             │
             │ HTTPS
             ▼

PRIVATE / SERVER
────────────────────────────────

FastAPI Backend
Gemini API key
JWT secret
Database credentials

             │
             ▼

PostgreSQL + Gemini
```

Private backend secrets must never cross into the browser application.

---

# 54. Next Documentation

After completing backend setup, continue with:

```text
docs/npm-integration.md
```

for complete React integration instructions.

Additional documentation:

```text
docs/environment-variables.md
docs/deployment.md
docs/troubleshooting.md
```

---

# License

Refer to the main Quantheonix repository for the project's current license and usage terms.