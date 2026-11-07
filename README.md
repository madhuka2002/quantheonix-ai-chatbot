# Quantheonix AI Chatbot

Quantheonix provides a FastAPI backend, a React/Vite system dashboard, and a
reusable React chatbot package. Assistant owners configure Gemini, OpenAI, or
Anthropic Claude in
the dashboard; provider credentials remain encrypted on the backend.

## Guides

- [Backend setup](docs/backend-setup.md) — FastAPI, PostgreSQL, Alembic, JWT,
  provider encryption, health checks, and backend Docker usage.
- [System frontend setup](docs/systemfrontend-setup.md) — the Quantheonix admin
  dashboard, login, AI Settings, and Test Chat.
- [Customer website widget](packages/quantheonix-chatbot/README.md) — install
  and connect `@quantheonix/chatbot` to a React website.
- [Self-hosted server](docs/self-hosted-setup.md) — private API/database,
  dashboard proxy, HTTPS, and data-preserving upgrades.
- [All run modes](docs/run-modes.md) — local Docker, hot reload, and server
  commands.

## Local Docker quick start

Run from the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
notepad .env
docker compose config
docker compose up --build --wait
docker compose ps
Invoke-RestMethod http://127.0.0.1:8080/api/v1/health
```

Open <http://127.0.0.1:8080>. Register or log in, select an assistant, configure
its provider, compatible model, and provider key in **AI Settings**, then use
**Test Chat**. Stop without deleting PostgreSQL data:

```powershell
docker compose down
```

## Customer website example

The package exports `QuantheonixChat` and `ChatWidget`. The supported public
integration uses `apiUrl` and `assistantId`:

```powershell
npm install @quantheonix/chatbot
```

```jsx
import { QuantheonixChat } from "@quantheonix/chatbot";
import "@quantheonix/chatbot/chatbot.css";

export default function App() {
  return (
    <QuantheonixChat
      apiUrl="https://chat-api.example.com"
      assistantId="YOUR_ASSISTANT_ID"
    />
  );
}
```

Provider keys, JWT secrets, and database credentials never belong in the
customer website or Vite environment.

## Security boundary

- Dashboard settings endpoints require JWT authentication and assistant
  ownership.
- Assistant provider keys are write-only, encrypted in PostgreSQL, and omitted
  from API responses and public widget configuration.
- `GEMINI_API_KEY` is an optional fallback only for explicitly grandfathered
  Gemini assistants; new accounts configure their own key.
- `PROVIDER_KEY_ENCRYPTION_SECRET` is required and must remain stable; losing or
  changing it prevents existing assistant keys from being decrypted.

Real `.env` files are ignored. Do not commit provider keys, JWT secrets,
database passwords, or the provider-key encryption secret.
