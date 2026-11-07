# Quantheonix system frontend setup

This guide covers the React/Vite admin dashboard in `frontend/`. It is the
system UI used to log in, manage assistants, configure AI providers, customize
the public widget, and test chat. Backend setup is documented separately in
[backend-setup.md](backend-setup.md).

## Requirements and install

Install Node.js 22 or newer. From the repository root in PowerShell:

```powershell
Set-Location frontend
npm ci
```

## Native Vite development

Create the public browser configuration:

```powershell
Copy-Item .env.example .env
notepad .env
```

For a native FastAPI server on port `8000`, use:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

This file may contain only public browser configuration. Never put Gemini,
OpenAI, or Anthropic keys, JWT signing secrets, database credentials, or
`PROVIDER_KEY_ENCRYPTION_SECRET` in the frontend environment.

Start Vite:

```powershell
npm run dev -- --host 127.0.0.1 --port 5173
```

Open <http://127.0.0.1:5173>. The backend must allow this exact origin in
`CORS_ORIGINS`.

## Docker dashboard and same-origin API proxy

From the repository root:

```powershell
Set-Location ..
Copy-Item .env.example .env
notepad .env
docker compose up --build --wait
```

Open <http://127.0.0.1:8080>. The production bundle uses the current browser
origin. Nginx proxies `/api/` to FastAPI and disables buffering for NDJSON chat
streams, so the bundle does not contain a localhost API URL.

## Registration to Test Chat

1. Register a normal user account or log in at the dashboard.
2. Open **Assistants** and create an assistant. The new assistant is selected
   automatically and **Configure AI** opens its AI Settings.
3. Choose Gemini, OpenAI, or Anthropic Claude.
4. Choose a suggested model or enter the exact model ID enabled for the
   provider account.
5. Enter that user's provider API key and save. The input clears and the page
   shows only whether a key is configured.
6. Open **Test Chat** and start a new conversation. Test Chat sends the
   selected assistant ID, so it uses that assistant's provider, model, prompt,
   temperature, and encrypted key.

The assistant selector controls AI Settings, customization, domains,
installation, and Test Chat. A user can read or change only assistants owned
by their authenticated account.

## AI Settings

For the selected assistant:

1. Choose **Google Gemini**, **OpenAI**, or **Anthropic Claude**.
2. Choose a suggested model or enter an exact provider model ID.
3. Enter a provider key to add or replace it, or select removal and save.
4. Save settings. The key field clears after saving and only the configured
   status is returned by the API.

Provider requests run in FastAPI. The browser never receives the stored key.
New assistants require an assistant-owned key. Only Gemini assistants that
predate self-service credentials can retain the explicitly grandfathered
server fallback. Changing providers always requires a new provider key.

Create and manage a Claude API key in the
[Claude Console](https://platform.claude.com/settings/keys). Keep it in the
masked AI Settings field only; do not put it in a frontend `.env` file.

Changing providers affects new conversations. Existing conversations remain
readable but are not replayed to a different provider.

## Test Chat

Conversation browser storage is namespaced by assistant. Changing providers
starts new conversations with the new provider; existing conversations remain
readable and are never silently replayed to a different provider.

## Quality checks

```powershell
Set-Location frontend
npm run lint
npm run build
```

## Customer website integration

The system dashboard is not the embeddable customer widget. Install and use
the published React package as documented in
[`packages/quantheonix-chatbot/README.md`](../packages/quantheonix-chatbot/README.md).
Its supported public props are `apiUrl` and `assistantId`.
Before installation, save each customer website hostname on the assistant's
**Allowed Domains** page. Widget sites do not need to be added to backend
`CORS_ORIGINS`, and saving a domain does not require a backend redeploy.
