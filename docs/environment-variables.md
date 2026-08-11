# Quantheonix AI Chatbot — Environment Variables

This document explains the environment variables required to configure and run the **Quantheonix AI Chatbot Backend**.

The Quantheonix system is separated into two main parts:

1. The React chatbot package — `@quantheonix/chatbot`
2. The Quantheonix backend API

The npm package runs inside the customer's frontend application, while sensitive configuration such as Gemini API keys, database credentials, and JWT secrets must remain on the backend.

---

# 1. Architecture Overview

The basic architecture is:

```text
Customer Website / React Application
                |
                |
                v
      @quantheonix/chatbot
                |
                | HTTPS API requests
                v
     Quantheonix Backend API
                |
        +-------+-------+
        |               |
        v               v
   PostgreSQL       Gemini API
```

The browser should **never communicate directly with Gemini using a secret API key**.

The frontend communicates with the Quantheonix backend.

The backend is responsible for:

- authentication
- authorization
- conversations
- messages
- streaming AI responses
- Gemini communication
- PostgreSQL access
- refresh tokens
- rate limiting
- security controls

---

# 2. Environment Files

The backend uses environment variables for configuration.

The repository provides safe example files:

```text
backend/.env.example
backend/.env.docker.example
```

These example files contain placeholders and may be committed to Git.

The real environment files are:

```text
backend/.env
backend/.env.docker
```

These files contain secrets and **must never be committed**.

---

# 3. Local Development Environment

When running the FastAPI backend directly on your computer, create:

```text
backend/.env
```

You can start from the example:

```bash
cd backend
cp .env.example .env
```

Then configure the values for your machine.

---

# 4. Docker Development Environment

When running the backend inside Docker, create:

```text
backend/.env.docker
```

Start from:

```bash
cd backend
cp .env.docker.example .env.docker
```

The Docker configuration may be different from the normal `.env`, especially for:

- PostgreSQL host
- CORS origins
- deployment configuration

---

# 5. Application Variables

## `APP_NAME`

Defines the name of the backend application.

Example:

```env
APP_NAME=Quantheonix AI Chatbot API
```

This value may be used by FastAPI for application metadata and documentation.

---

## `APP_VERSION`

Defines the current backend version.

Example:

```env
APP_VERSION=1.0.0
```

The version should be updated when releasing significant backend versions.

---

## `ENVIRONMENT`

Describes the environment where the backend is running.

Development:

```env
ENVIRONMENT=development
```

Production:

```env
ENVIRONMENT=production
```

Other environments may also be used when required, for example:

```text
testing
staging
```

---

## `DEBUG`

Controls development/debug behavior.

Development:

```env
DEBUG=true
```

Production:

```env
DEBUG=false
```

The current Quantheonix backend uses the debug setting when configuring application behavior such as logging and API documentation.

For example, the FastAPI Swagger and ReDoc interfaces are available when debug mode is enabled.

Production deployments should normally use:

```env
DEBUG=false
```

---

## `API_V1_PREFIX`

Defines the prefix used by version 1 API routes.

Default:

```env
API_V1_PREFIX=/api/v1
```

This produces endpoints such as:

```text
/api/v1/auth/login
/api/v1/chat/stream
/api/v1/health
```

Changing this value changes the API prefix expected by clients.

For normal installations, keeping the default is recommended.

---

# 6. Gemini AI Configuration

The Quantheonix backend uses Gemini for AI response generation.

Gemini credentials belong **only on the backend**.

---

## `GEMINI_API_KEY`

The API key used by the backend to communicate with Gemini.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace:

```text
your_gemini_api_key
```

with your actual Gemini API key.

### Security

Never place the Gemini API key inside:

```text
React source code
Vite public environment variables
JavaScript bundles
@quantheonix/chatbot configuration
GitHub repositories
public configuration files
```

The correct architecture is:

```text
Browser
   |
   v
Quantheonix Backend
   |
   | Secret Gemini API Key
   v
Gemini
```

Not:

```text
Browser
   |
   | Secret Gemini API Key
   v
Gemini
```

---

## `GEMINI_MODEL`

Defines which Gemini model the backend should use.

Example:

```env
GEMINI_MODEL=gemini-flash-latest
```

The available Gemini models may change over time.

The configured model must be available to the Gemini API account associated with `GEMINI_API_KEY`.

---

## `GEMINI_TEMPERATURE`

Controls the model response temperature.

Example:

```env
GEMINI_TEMPERATURE=0.7
```

The temperature influences how variable the generated responses may be.

The default Quantheonix configuration uses:

```text
0.7
```

---

# 7. PostgreSQL Configuration

Quantheonix uses PostgreSQL to persist application data.

The backend connects to PostgreSQL using SQLAlchemy and the asynchronous PostgreSQL driver.

---

## `DATABASE_URL`

Defines the PostgreSQL connection URL.

General format:

```text
postgresql+asyncpg://USERNAME:PASSWORD@HOST:PORT/DATABASE
```

Example:

```env
DATABASE_URL=postgresql+asyncpg://quantheonix_user:YOUR_DB_PASSWORD@localhost:5432/quantheonix_chatbot
```

Replace:

```text
YOUR_DB_PASSWORD
```

with the password configured for your PostgreSQL user.

---

# 8. Local PostgreSQL Configuration

If both the FastAPI backend and PostgreSQL are running directly on the same computer, use:

```text
localhost
```

as the database host.

Example structure:

```text
postgresql+asyncpg://USERNAME:PASSWORD@localhost:5432/DATABASE
```

A typical Quantheonix development configuration therefore looks like:

```env
DATABASE_URL=postgresql+asyncpg://quantheonix_user:YOUR_DB_PASSWORD@localhost:5432/quantheonix_chatbot
```

Architecture:

```text
Windows / Linux / macOS Host
│
├── FastAPI Backend
│
└── PostgreSQL
      |
      └── quantheonix_chatbot
```

---

# 9. Docker PostgreSQL Configuration

A common development setup is:

```text
FastAPI Backend -> Docker
PostgreSQL      -> Host computer
```

Inside a Docker container:

```text
localhost
```

refers to the container itself.

It does **not** refer to the Windows host.

Therefore this would normally be incorrect for that setup:

```text
postgresql+asyncpg://USERNAME:PASSWORD@localhost:5432/DATABASE
```

When PostgreSQL runs on the host while the backend runs inside Docker, use:

```text
host.docker.internal
```

Example:

```env
DATABASE_URL=postgresql+asyncpg://quantheonix_user:YOUR_DB_PASSWORD@host.docker.internal:5432/quantheonix_chatbot
```

Architecture:

```text
Docker Container
│
│ Quantheonix Backend
│
│ host.docker.internal
│
v
Host Computer
│
└── PostgreSQL
      |
      └── quantheonix_chatbot
```

---

# 10. Database Credentials

Database credentials are sensitive.

Never commit a real value such as:

```text
DATABASE_URL=postgresql+asyncpg://real_user:real_password@...
```

to Git.

Instead, example files should use placeholders:

```env
DATABASE_URL=postgresql+asyncpg://quantheonix_user:YOUR_DB_PASSWORD@localhost:5432/quantheonix_chatbot
```

Each installation should provide its own PostgreSQL credentials.

---

# 11. JWT Authentication

Quantheonix uses JWT-based authentication.

The backend issues access tokens and refresh tokens.

---

## `JWT_SECRET_KEY`

Secret used by the backend when signing JWT tokens.

Example:

```env
JWT_SECRET_KEY=replace_with_a_secure_random_secret
```

This value must be private.

Do not use a simple value such as:

```text
password
secret
123456
jwtsecret
```

Generate a strong random value.

Python can generate one:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the generated value into:

```env
JWT_SECRET_KEY=YOUR_GENERATED_SECRET
```

### Important

Do not:

- commit the JWT secret
- expose it to React
- include it in the npm package
- send it to the browser
- publish it in documentation
- reuse an accidentally exposed secret

Production should use its own secret.

---

## `JWT_ALGORITHM`

Defines the JWT signing algorithm.

Current default:

```env
JWT_ALGORITHM=HS256
```

Unless the backend implementation is changed accordingly, keep:

```text
HS256
```

---

# 12. Access Token Expiration

## `ACCESS_TOKEN_EXPIRE_MINUTES`

Defines how long an access token remains valid.

Default:

```env
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Therefore an access token normally expires after:

```text
30 minutes
```

The frontend may obtain another access token using the application's refresh-token flow.

---

# 13. Refresh Token Expiration

## `REFRESH_TOKEN_EXPIRE_DAYS`

Defines the refresh-token lifetime.

Default:

```env
REFRESH_TOKEN_EXPIRE_DAYS=7
```

This allows the authentication system to maintain sessions without requiring the user to enter credentials whenever a short-lived access token expires.

---

# 14. CORS Configuration

## `CORS_ORIGINS`

CORS stands for:

```text
Cross-Origin Resource Sharing
```

It controls which browser origins are allowed to communicate with the backend.

This is especially important because the npm chatbot package runs inside another website.

The value must be a JSON-style list.

General format:

```text
CORS_ORIGINS=["ORIGIN_1","ORIGIN_2"]
```

---

# 15. Local Development CORS

A local Vite frontend commonly runs on port:

```text
5173
```

Vite preview commonly uses:

```text
4173
```

Therefore the local development configuration should permit the required local frontend origins.

For example, the configuration may include:

```text
localhost:5173
127.0.0.1:5173
localhost:4173
127.0.0.1:4173
```

with the appropriate HTTP scheme.

The important rule is:

> `CORS_ORIGINS` must contain the actual browser origin hosting the frontend.

---

# 16. Docker Development CORS

When the Docker frontend is exposed on:

```text
8080
```

the Docker environment should additionally allow the required port `8080` origins.

A Docker development configuration may therefore allow origins corresponding to:

```text
localhost:8080
127.0.0.1:8080

localhost:5173
127.0.0.1:5173

localhost:4173
127.0.0.1:4173
```

with the appropriate HTTP scheme.

---

# 17. Production CORS

Suppose a customer's website is:

```text
https://example.com
```

The production backend should allow:

```text
https://example.com
```

If the application is also served through:

```text
https://www.example.com
```

then both origins may be required.

Example:

```env
CORS_ORIGINS=["https://example.com","https://www.example.com"]
```

### Important

These are different origins:

```text
https://example.com
https://www.example.com
```

If both are used, both may need to be configured.

---

# 18. Do Not Use Wildcard CORS Without a Reason

Avoid production configuration such as:

```text
*
```

unless the application architecture specifically requires unrestricted cross-origin access and the security consequences have been considered.

For the Quantheonix chatbot, the recommended production approach is to explicitly list trusted websites.

For example:

```text
Customer Website
        |
        | allowed
        v
Quantheonix Backend

Unknown Website
        |
        | blocked by CORS policy
        X
Quantheonix Backend
```

---

# 19. Rate Limiting

Quantheonix includes application-level rate limiting.

Rate limiting helps protect endpoints against excessive request traffic.

---

## `RATE_LIMIT_ENABLED`

Enables or disables application rate limiting.

Recommended:

```env
RATE_LIMIT_ENABLED=true
```

For normal deployments, rate limiting should remain enabled.

---

## `RATE_LIMIT_LOGIN_REQUESTS`

Maximum login requests permitted within the configured rate-limit window.

Default:

```env
RATE_LIMIT_LOGIN_REQUESTS=10
```

---

## `RATE_LIMIT_REGISTER_REQUESTS`

Maximum registration requests permitted within the configured rate-limit window.

Default:

```env
RATE_LIMIT_REGISTER_REQUESTS=5
```

---

## `RATE_LIMIT_REFRESH_REQUESTS`

Maximum refresh-token requests permitted within the configured rate-limit window.

Default:

```env
RATE_LIMIT_REFRESH_REQUESTS=30
```

---

## `RATE_LIMIT_CHAT_REQUESTS`

Maximum chat requests permitted within the configured rate-limit window.

Default:

```env
RATE_LIMIT_CHAT_REQUESTS=20
```

---

## `RATE_LIMIT_WINDOW_SECONDS`

Defines the length of the rate-limit window.

Default:

```env
RATE_LIMIT_WINDOW_SECONDS=60
```

Therefore the default window is:

```text
60 seconds
```

---

# 20. Rate-Limit Configuration Summary

Default configuration:

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_LOGIN_REQUESTS=10
RATE_LIMIT_REGISTER_REQUESTS=5
RATE_LIMIT_REFRESH_REQUESTS=30
RATE_LIMIT_CHAT_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
```

These values may be adjusted according to deployment requirements.

---

# 21. Complete Local Environment Template

A local installation generally requires the following configuration:

```env
# --------------------------------------------------
# Application
# --------------------------------------------------

APP_NAME=Quantheonix AI Chatbot API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
API_V1_PREFIX=/api/v1


# --------------------------------------------------
# Gemini
# --------------------------------------------------

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-flash-latest
GEMINI_TEMPERATURE=0.7


# --------------------------------------------------
# PostgreSQL
# --------------------------------------------------

DATABASE_URL=postgresql+asyncpg://quantheonix_user:YOUR_DB_PASSWORD@localhost:5432/quantheonix_chatbot


# --------------------------------------------------
# JWT
# --------------------------------------------------

JWT_SECRET_KEY=YOUR_SECURE_RANDOM_JWT_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7


# --------------------------------------------------
# CORS
# --------------------------------------------------

CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:4173","http://127.0.0.1:4173"]


# --------------------------------------------------
# Rate Limiting
# --------------------------------------------------

RATE_LIMIT_ENABLED=true
RATE_LIMIT_LOGIN_REQUESTS=10
RATE_LIMIT_REGISTER_REQUESTS=5
RATE_LIMIT_REFRESH_REQUESTS=30
RATE_LIMIT_CHAT_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
```

---

# 22. Complete Docker Environment Template

When the backend runs inside Docker while PostgreSQL runs on the host:

```env
# --------------------------------------------------
# Application
# --------------------------------------------------

APP_NAME=Quantheonix AI Chatbot API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
API_V1_PREFIX=/api/v1


# --------------------------------------------------
# Gemini
# --------------------------------------------------

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-flash-latest
GEMINI_TEMPERATURE=0.7


# --------------------------------------------------
# PostgreSQL
# --------------------------------------------------

DATABASE_URL=postgresql+asyncpg://quantheonix_user:YOUR_DB_PASSWORD@host.docker.internal:5432/quantheonix_chatbot


# --------------------------------------------------
# JWT
# --------------------------------------------------

JWT_SECRET_KEY=YOUR_SECURE_RANDOM_JWT_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7


# --------------------------------------------------
# CORS
# --------------------------------------------------

CORS_ORIGINS=["http://localhost:8080","http://127.0.0.1:8080","http://localhost:5173","http://127.0.0.1:5173","http://localhost:4173","http://127.0.0.1:4173"]


# --------------------------------------------------
# Rate Limiting
# --------------------------------------------------

RATE_LIMIT_ENABLED=true
RATE_LIMIT_LOGIN_REQUESTS=10
RATE_LIMIT_REGISTER_REQUESTS=5
RATE_LIMIT_REFRESH_REQUESTS=30
RATE_LIMIT_CHAT_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
```

---

# 23. Local vs Docker Configuration

The most important difference is the database host.

| Backend Location | PostgreSQL Location | Database Host |
|---|---|---|
| Host computer | Same host | `localhost` |
| Docker | Host computer | `host.docker.internal` |

CORS also changes according to where the frontend is running.

For example:

| Frontend | Common Development Port |
|---|---:|
| Vite development | `5173` |
| Vite preview | `4173` |
| Quantheonix Docker frontend | `8080` |

These ports are development defaults for this project and may be changed if required.

---

# 24. npm Package and Environment Variables

Installing the npm package:

```bash
npm install @quantheonix/chatbot
```

does **not** automatically create the backend infrastructure.

The npm package provides the embeddable React chatbot UI/client.

A running Quantheonix backend is still required.

The complete architecture is:

```text
npm Package
     |
     | apiUrl
     v
Quantheonix Backend
     |
     +---------------------+
     |                     |
     v                     v
PostgreSQL             Gemini API
```

---

# 25. What the npm Package User Needs

A developer integrating the package needs:

```text
1. @quantheonix/chatbot
2. A running Quantheonix backend
3. The backend URL
4. Authentication integration when protected endpoints are used
```

The developer does **not** provide these secrets to the npm package:

```text
GEMINI_API_KEY
JWT_SECRET_KEY
DATABASE_URL
PostgreSQL password
```

Those belong to the backend deployment.

---

# 26. React Package Example

After installing:

```bash
npm install @quantheonix/chatbot
```

the application can import the component:

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

function App() {
  return (
    <QuantheonixChat
      apiUrl="YOUR_BACKEND_URL"
      title="AI Assistant"
    />
  );
}

export default App;
```

`YOUR_BACKEND_URL` represents the URL where the Quantheonix backend has been deployed.

The API URL is not a Gemini API key.

---

# 27. Authentication Integration

The chatbot package supports an access token and an access-token provider.

For applications that already have an access token, it can be supplied to the component.

Conceptually:

```jsx
<QuantheonixChat
  apiUrl="YOUR_BACKEND_URL"
  accessToken={accessToken}
/>
```

For applications that need automatic token retrieval or refresh, the package supports:

```text
getAccessToken
```

This allows the host application to control authentication without exposing backend signing secrets.

The JWT secret always remains on the backend.

---

# 28. Production Example

A production architecture may look like:

```text
Customer Website
https://example.com
        |
        |
        v
@quantheonix/chatbot
        |
        | HTTPS
        v
AI Backend
        |
        +-------------------+
        |                   |
        v                   v
Managed PostgreSQL      Gemini API
```

The production backend environment would contain configuration such as:

```text
ENVIRONMENT=production
DEBUG=false

GEMINI_API_KEY=<secret>

DATABASE_URL=<production database>

JWT_SECRET_KEY=<production secret>

CORS_ORIGINS=<customer website origins>
```

Production credentials should normally be stored using the hosting provider's environment-variable or secret-management system rather than committed files.

---

# 29. `.env.example`

The repository contains:

```text
backend/.env.example
```

This file is intended for developers running the backend directly.

It should contain:

- configuration names
- development defaults
- placeholder secrets

It must not contain real credentials.

---

# 30. `.env.docker.example`

The repository also contains:

```text
backend/.env.docker.example
```

This file is intended for Docker-based development.

Its database URL may use:

```text
host.docker.internal
```

when PostgreSQL runs on the host.

Again, it must contain only placeholder credentials.

---

# 31. `.gitignore`

The real files should remain ignored:

```text
backend/.env
backend/.env.docker
```

The example files should remain trackable:

```text
backend/.env.example
backend/.env.docker.example
```

Before committing, verify:

```bash
git check-ignore backend/.env
git check-ignore backend/.env.docker
```

Both should be ignored.

You can also check that real environment files are not tracked:

```bash
git ls-files | grep -E '(^|/)\.env($|\.docker$)'
```

Ideally, this command should return no real secret environment files.

---

# 32. Credential Rotation

If a credential is accidentally:

- committed
- published
- uploaded publicly
- included in documentation
- included in an npm package
- shared somewhere it should not have been

do not simply delete the text and continue using the credential.

Rotate the credential.

For example:

```text
Old Gemini API key
        |
        v
Revoke / disable
        |
        v
Generate new key
        |
        v
Update backend environment
```

The same principle applies to:

- JWT secrets
- database passwords
- API keys
- deployment secrets

---

# 33. Production Security Checklist

Before deploying Quantheonix:

- [ ] `DEBUG=false`
- [ ] New production Gemini API key configured
- [ ] Strong production JWT secret configured
- [ ] Production PostgreSQL credentials configured
- [ ] Production database is not publicly exposed unnecessarily
- [ ] CORS contains only trusted frontend origins
- [ ] HTTPS is enabled
- [ ] `.env` is not committed
- [ ] `.env.docker` is not committed
- [ ] No API keys exist in frontend source
- [ ] No JWT secret exists in frontend source
- [ ] No database password exists in frontend source
- [ ] Rate limiting is enabled
- [ ] Backend health endpoint works
- [ ] Authentication works
- [ ] Token refresh works
- [ ] Chat streaming works
- [ ] Backend logs do not expose secrets

---

# 34. Development Security Checklist

For development:

- [ ] PostgreSQL is running
- [ ] Database exists
- [ ] Database user exists
- [ ] `.env` has the correct database password
- [ ] Gemini API key is configured
- [ ] JWT secret is configured
- [ ] Local frontend origin is included in CORS
- [ ] `.env` is ignored by Git
- [ ] `.env.docker` is ignored by Git

---

# 35. Troubleshooting

## Backend cannot connect to PostgreSQL

Check:

```text
DATABASE_URL
```

If the backend runs directly on your computer, the host will commonly be:

```text
localhost
```

If the backend runs in Docker while PostgreSQL runs on the host, the host will commonly be:

```text
host.docker.internal
```

Also verify:

- PostgreSQL is running
- port `5432` is accessible
- username is correct
- password is correct
- database exists

---

## Browser reports a CORS error

Check:

```text
CORS_ORIGINS
```

The exact frontend origin must be allowed.

Remember that these are different origins:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Also remember that production domains using HTTPS are different from local HTTP origins.

Restart the backend after changing environment configuration.

---

## Authentication fails after changing `JWT_SECRET_KEY`

Existing tokens were signed using the previous secret.

Changing the secret invalidates tokens created using the old secret.

Users may therefore need to authenticate again.

---

## Gemini requests fail

Check:

```text
GEMINI_API_KEY
GEMINI_MODEL
```

Verify that:

- the API key is valid
- the configured model is available
- the account has available quota
- the backend can reach the Gemini API

---

## Docker backend cannot reach PostgreSQL

If PostgreSQL is running on the host and the backend is running in Docker, verify that the database host is configured appropriately for Docker rather than assuming that container `localhost` refers to the host computer.

---

# 36. Environment Variable Reference

| Variable | Required | Sensitive | Example / Default |
|---|---|---|---|
| `APP_NAME` | No | No | `Quantheonix AI Chatbot API` |
| `APP_VERSION` | No | No | `1.0.0` |
| `ENVIRONMENT` | Depends on configuration | No | `development` |
| `DEBUG` | No | No | `true` / `false` |
| `API_V1_PREFIX` | No | No | `/api/v1` |
| `GEMINI_API_KEY` | Yes | **Yes** | User-provided secret |
| `GEMINI_MODEL` | No | No | `gemini-flash-latest` |
| `GEMINI_TEMPERATURE` | No | No | `0.7` |
| `DATABASE_URL` | Yes | **Yes** | PostgreSQL connection URL |
| `JWT_SECRET_KEY` | Yes | **Yes** | Random secret |
| `JWT_ALGORITHM` | No | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | No | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | No | `7` |
| `CORS_ORIGINS` | Yes for browser clients | No | JSON list of trusted origins |
| `RATE_LIMIT_ENABLED` | No | No | `true` |
| `RATE_LIMIT_LOGIN_REQUESTS` | No | No | `10` |
| `RATE_LIMIT_REGISTER_REQUESTS` | No | No | `5` |
| `RATE_LIMIT_REFRESH_REQUESTS` | No | No | `30` |
| `RATE_LIMIT_CHAT_REQUESTS` | No | No | `20` |
| `RATE_LIMIT_WINDOW_SECONDS` | No | No | `60` |

---

# 37. Recommended Deployment Principle

Keep responsibilities separated:

```text
FRONTEND
-----------------------------
React application
@quantheonix/chatbot
Backend API URL
Access-token integration


BACKEND
-----------------------------
Gemini API key
JWT secret
Authentication
Rate limiting
Chat processing
Database access


DATABASE
-----------------------------
Users
Conversations
Messages
Authentication-related data
Persistent application data
```

The frontend must never need direct access to backend secrets.

---

# 38. Final Rule

The most important environment-security rule for Quantheonix is:

> Public frontend configuration tells the chatbot **where the backend is**. Private backend configuration tells the backend **how to access protected services**.

Therefore:

```text
apiUrl
```

can be provided to the npm component.

But values such as:

```text
GEMINI_API_KEY
JWT_SECRET_KEY
DATABASE_URL
```

must remain private on the backend.

---

# Related Documentation

See also:

```text
docs/backend-setup.md
backend/.env.example
backend/.env.docker.example
packages/quantheonix-chatbot/README.md
```

The npm package installation and integration guide explains how a frontend application connects to a configured Quantheonix backend.