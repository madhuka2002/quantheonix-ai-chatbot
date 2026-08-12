# Quantheonix AI Chatbot

A reusable AI chatbot platform consisting of an embeddable React widget and a self-hosted FastAPI backend.

Quantheonix is designed for developers who want to add an AI chatbot to a React application without exposing AI provider credentials, database credentials, or authentication secrets in the browser.

The project provides:

- an embeddable React chatbot widget
- streaming AI responses
- Markdown and syntax-highlighted code rendering
- JWT authentication support
- access-token refresh integration
- conversation persistence
- PostgreSQL storage
- Gemini AI integration
- rate limiting
- Docker-based self-hosting
- automatic database migrations

---

## Project Status

Current release:

```text
@quantheonix/chatbot v0.1.0
```

The frontend widget is packaged separately from the backend.

```text
React Application
        |
        | @quantheonix/chatbot
        |
        v
Quantheonix Backend
        |
        +----------------------+
        |                      |
        v                      v
   PostgreSQL              Gemini API
```

The browser never communicates directly with Gemini.

---

# Features

## Frontend Widget

- Reusable React component
- Streaming AI responses
- NDJSON stream processing
- Markdown rendering
- GitHub-flavored Markdown
- Syntax-highlighted code blocks
- Configurable title
- Configurable welcome message
- Configurable input placeholder
- Bottom-right positioning
- Bottom-left positioning
- Responsive mobile layout
- Stop generation
- New chat
- Conversation ID management
- JWT access-token support
- Token refresh integration
- Automatic retry after HTTP `401`
- Error handling

## Backend

- FastAPI REST API
- Async PostgreSQL access
- SQLAlchemy
- Alembic database migrations
- Gemini AI integration
- JWT authentication
- Access and refresh tokens
- Conversation ownership
- Persistent conversations
- Persistent messages
- Streaming responses
- Request rate limiting
- CORS configuration
- Health monitoring
- Docker deployment

---

# Repository Structure

```text
quantheonix-ai-chatbot/
│
├── backend/
│   ├── alembic/
│   ├── app/
│   ├── scripts/
│   ├── tests/
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── main.py
│   ├── pytest.ini
│   └── requirements.txt
│
├── frontend/
│
├── packages/
│   └── quantheonix-chatbot/
│       ├── dist/
│       ├── README.md
│       └── package.json
│
├── widget-demo/
│
├── docs/
│   ├── self-hosted-setup.md
│   └── troubleshooting.md
│
├── .env.selfhosted.example
├── compose.selfhosted.yaml
├── compose.yaml
└── README.md
```

---

# Quick Start

There are two main parts to Quantheonix:

1. Quantheonix backend
2. `@quantheonix/chatbot` React widget

For a complete installation, start the backend first and then connect the React widget to it.

---

# 1. Self-Host the Backend

Clone the repository:

```bash
git clone https://github.com/madhuka2002/quantheonix-ai-chatbot.git
cd quantheonix-ai-chatbot
```

Create the self-hosted environment file:

```bash
cp .env.selfhosted.example .env.selfhosted
```

Open `.env.selfhosted` and configure the required values.

At minimum, configure:

```env
POSTGRES_DB=quantheonix_chatbot
POSTGRES_USER=quantheonix_user
POSTGRES_PASSWORD=replace_with_a_strong_database_password

GEMINI_API_KEY=replace_with_your_gemini_api_key

JWT_SECRET_KEY=replace_with_a_long_random_secret

CORS_ORIGINS=["http://localhost:5173"]
```

Generate a strong JWT secret using Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Do not commit `.env.selfhosted`.

---

# 2. Start the Backend

Make sure Docker is running.

Then execute:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  up -d --build
```

Docker will:

1. start PostgreSQL
2. wait for PostgreSQL to become healthy
3. run Alembic database migrations
4. start the FastAPI backend
5. expose the API on port `8000`

Check the containers:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  ps
```

The PostgreSQL and backend containers should report healthy states.

---

# 3. Verify the Backend

Check the API health endpoint:

```bash
curl http://localhost:8000/api/v1/health
```

A healthy installation should return a response similar to:

```json
{
  "status": "healthy",
  "service": "Quantheonix AI Chatbot API",
  "version": "1.0.0",
  "database": "connected"
}
```

You can also inspect backend logs:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs backend
```

On a fresh database, Alembic migrations are applied automatically before the API starts.

If a migration fails, backend startup is stopped instead of continuing with an invalid database state.

For detailed instructions, see:

```text
docs/self-hosted-setup.md
```

---

# 4. Install the React Widget

In your React application:

```bash
npm install @quantheonix/chatbot
```

Import the component and stylesheet:

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";
```

Use it in your application:

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

The chatbot now communicates with your self-hosted Quantheonix backend.

---

# Frontend Environment Variable

For Vite applications, storing the backend URL in an environment variable is recommended.

Create:

```text
.env
```

and add:

```env
VITE_CHATBOT_API_URL=http://localhost:8000
```

Then:

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

function App() {
  return (
    <QuantheonixChat
      apiUrl={
        import.meta.env.VITE_CHATBOT_API_URL
      }
    />
  );
}

export default App;
```

For production:

```env
VITE_CHATBOT_API_URL=https://api.example.com
```

The backend URL is public configuration and is not a secret.

---

# Widget Configuration

The main component is:

```jsx
<QuantheonixChat />
```

Supported properties include:

| Prop | Type | Required | Default | Description |
| --- | --- | ---: | --- | --- |
| `apiUrl` | `string` | Yes | — | Quantheonix backend URL |
| `accessToken` | `string \| null` | No | `null` | JWT access token |
| `getAccessToken` | `function \| null` | No | `null` | Callback for obtaining or refreshing an access token |
| `title` | `string` | No | `"Quantheonix AI"` | Widget title |
| `welcomeMessage` | `string` | No | `"Hello! How can I help you?"` | Initial assistant message |
| `placeholder` | `string` | No | `"Type your message..."` | Message input placeholder |
| `initiallyOpen` | `boolean` | No | `false` | Start widget open |
| `position` | `string` | No | `"bottom-right"` | Widget placement |

Example:

```jsx
<QuantheonixChat
  apiUrl="http://localhost:8000"
  title="Support Assistant"
  welcomeMessage="Hello! How can we help?"
  placeholder="Ask a question..."
  initiallyOpen={false}
  position="bottom-right"
/>
```

---

# Authentication

The widget supports JWT authentication.

If your application already has an access token:

```jsx
function App() {
  const accessToken =
    localStorage.getItem("access_token");

  return (
    <QuantheonixChat
      apiUrl="http://localhost:8000"
      accessToken={accessToken}
    />
  );
}
```

Requests include:

```http
Authorization: Bearer ACCESS_TOKEN
```

---

# Token Refresh

Applications that support refresh tokens should use `getAccessToken`.

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
    "http://localhost:8000/api/v1/auth/refresh",
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
  apiUrl="http://localhost:8000"
  getAccessToken={getAccessToken}
/>
```

When the backend returns `401`, the widget can request a refreshed token and retry the chat request.

---

# Streaming

Chat responses are streamed from:

```text
/api/v1/chat/stream
```

using:

```text
application/x-ndjson
```

Example events:

```json
{
  "type": "start",
  "conversation_id": "..."
}
```

```json
{
  "type": "chunk",
  "text": "Hello"
}
```

```json
{
  "type": "done",
  "conversation_id": "..."
}
```

The widget progressively renders the assistant response as chunks arrive.

---

# Conversations

The backend creates and persists conversations.

Typical flow:

```text
First message
      |
      v
Backend creates conversation
      |
      v
conversation_id returned
      |
      v
Widget stores conversation_id
      |
      v
Future messages continue conversation
```

Selecting **New chat** clears the current client-side conversation state and starts a new conversation on the next request.

---

# AI Provider

Quantheonix currently integrates with Gemini through the backend.

Example configuration:

```env
GEMINI_MODEL=gemini-flash-latest
GEMINI_TEMPERATURE=0.7
```

The Gemini API key must remain on the backend.

Never place:

```env
GEMINI_API_KEY=...
```

inside a frontend application.

---

# Database

Quantheonix uses PostgreSQL.

The self-hosted deployment supports configurable:

```env
POSTGRES_DB=quantheonix_chatbot
POSTGRES_USER=quantheonix_user
POSTGRES_PASSWORD=...
```

The backend constructs its database connection using the self-hosted PostgreSQL service.

Database schema changes are managed with Alembic.

---

# Database Migrations

The Docker self-hosted deployment automatically executes:

```bash
alembic upgrade head
```

before starting FastAPI.

The startup sequence is:

```text
PostgreSQL starts
       |
       v
PostgreSQL becomes healthy
       |
       v
Alembic migrations run
       |
       +---- failure ----> backend stops
       |
       v
Uvicorn starts
       |
       v
API becomes healthy
```

You normally do not need to run Alembic manually when using the self-hosted Docker configuration.

---

# CORS

The backend only accepts browser requests from configured origins.

Example:

```env
CORS_ORIGINS=["http://localhost:5173"]
```

Multiple origins:

```env
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","https://example.com"]
```

For production, add your real frontend domain.

Do not use Markdown-style links inside this value.

Correct:

```env
CORS_ORIGINS=["https://example.com"]
```

Incorrect:

```text
["[https://example.com](https://example.com)"]
```

---

# Rate Limiting

The backend supports configurable request rate limits.

Self-hosted environment variables include settings for:

- chat requests
- login requests
- registration requests
- refresh-token requests
- rate-limit window duration

Rate limiting should remain enabled in production.

---

# Security

Keep all sensitive credentials on the backend.

Never expose the following in frontend code:

```text
GEMINI_API_KEY
JWT_SECRET_KEY
POSTGRES_PASSWORD
DATABASE_URL
```

Recommended practices:

- use strong unique database passwords
- generate a long random JWT secret
- use HTTPS in production
- restrict CORS to trusted domains
- keep `.env` files outside Git
- rotate credentials if they are accidentally exposed
- keep Docker images and dependencies updated
- keep rate limiting enabled
- use separate production credentials

---

# Environment Files

The repository may contain example environment files such as:

```text
.env.selfhosted.example
backend/.env.example
backend/.env.docker.example
```

These files contain placeholders only.

Actual environment files should not be committed.

Examples:

```text
.env.selfhosted
backend/.env
backend/.env.docker
frontend/.env
```

---

# Stop the Self-Hosted Stack

Stop containers:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  down
```

This keeps the PostgreSQL volume.

---

# Completely Reset the Database

> Warning: this permanently deletes the PostgreSQL data stored in the Docker volume.

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  down -v
```

Then restart:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  up -d --build
```

This creates a fresh PostgreSQL database and reruns all migrations.

---

# Updating a Self-Hosted Installation

Pull the latest code:

```bash
git pull
```

Then rebuild:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  up -d --build
```

Alembic applies any new database migrations during backend startup.

---

# Logs

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

Follow backend logs:

```bash
docker compose \
  --env-file .env.selfhosted \
  -f compose.selfhosted.yaml \
  logs -f backend
```

---

# Development

## Backend Tests

From the backend development environment:

```bash
pytest -v
```

Current backend tests cover areas including:

- rate limiting
- access-token handling
- refresh-token handling
- token-type validation

## Widget

From:

```text
packages/quantheonix-chatbot
```

run:

```bash
npm install
npm run lint
npm run build
```

Test package contents:

```bash
npm pack --dry-run
```

---

# Troubleshooting

If something fails, see:

```text
docs/troubleshooting.md
```

Common problems include:

- Docker not running
- incorrect PostgreSQL credentials
- an old PostgreSQL Docker volume
- database migration failure
- CORS errors
- expired access tokens
- Gemini API errors
- Gemini quota limits
- incorrect backend URL
- port conflicts

---

# Documentation

Detailed documentation:

```text
docs/self-hosted-setup.md
docs/troubleshooting.md
packages/quantheonix-chatbot/README.md
```

---

# Technology Stack

## Frontend Package

- React
- Vite
- react-markdown
- remark-gfm
- rehype-highlight
- highlight.js

## Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- asyncpg
- Alembic
- PostgreSQL
- Gemini API
- JWT authentication

## Deployment

- Docker
- Docker Compose
- PostgreSQL 17 Alpine

---

# License

This project is licensed under the MIT License.

---

# Author

Developed as part of the Quantheonix project ecosystem.

GitHub:

```text
https://github.com/madhuka2002/quantheonix-ai-chatbot
```

npm package:

```text
@quantheonix/chatbot
```