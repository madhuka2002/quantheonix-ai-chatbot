# Problem and solution

## The frontend problem

Adding an AI chatbot to a React website is more than drawing a chat window. A
frontend developer otherwise has to build the widget UI, connect and secure an
AI provider, stream partial responses, preserve conversation history, and keep
provider/database credentials out of the browser.

## My solution

Quantheonix separates those responsibilities into a reusable system:

1. Set up the [FastAPI backend](docs/backend-setup.md) and the
   [system dashboard](docs/systemfrontend-setup.md).
2. In the dashboard, create or select an assistant, configure Gemini, OpenAI,
   or Anthropic Claude,
   choose its model, store its encrypted provider key, and test it.
3. In a customer React website, follow the
   [`@quantheonix/chatbot` guide](packages/quantheonix-chatbot/README.md), run
   `npm install @quantheonix/chatbot`, import its stylesheet, and connect the
   widget with the public API URL and assistant ID.

The website receives streaming chat behavior and conversation memory without
holding provider credentials or reimplementing the backend.

## Tech stack, skills, and methods

| Item | How I used it |
|---|---|
| FastAPI | Authenticated assistant management plus public and private chat APIs; provider calls remain server-side. |
| React and Vite | Admin dashboard, AI Settings, Test Chat, and the reusable React widget build. |
| PostgreSQL and SQLAlchemy | Persistent users, assistants, encrypted provider keys, conversations, messages, and widget settings. |
| Alembic | Data-preserving schema migrations, including provider and conversation snapshots. |
| JWT | Dashboard authentication and ownership-protected assistant settings. |
| npm packaging | `@quantheonix/chatbot` exports a reusable component and stylesheet for customer React sites. |
| NDJSON streaming | Incremental authenticated and public widget responses while retaining the existing API contract. |
| Docker Compose and Nginx | Reproducible API/database/dashboard stacks and a same-origin streaming `/api/` proxy. |
| pytest and GitHub Actions | Isolated PostgreSQL integration tests, mocked providers, frontend validation, and two-stack smoke CI. |

For a self-hosted deployment and HTTPS proxy, use the
[server guide](docs/self-hosted-setup.md).
