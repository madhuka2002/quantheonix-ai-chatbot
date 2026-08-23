# @quantheonix/chatbot

Embeddable React chatbot widget for assistants created with the Quantheonix AI Chatbot platform.

The widget loads its configuration from the Quantheonix backend and supports streaming AI responses, conversation memory, Markdown rendering, syntax highlighting, custom appearance, and allowed-domain protection.

> A running Quantheonix backend and an active assistant are required.

## Features

- React chatbot widget
- Public assistant configuration loading
- Streaming AI responses using NDJSON
- Conversation memory
- Markdown rendering
- GitHub-flavored Markdown
- Syntax-highlighted code blocks
- Stop generation
- New chat
- Configurable colors and appearance
- Configurable dimensions and fonts
- Bottom-left or bottom-right placement
- Custom avatar and launcher support
- Allowed-domain validation
- Responsive layout
- Public chatbot access without exposing user JWT tokens

## Requirements

- React 18 or newer
- React DOM 18 or newer
- Quantheonix backend
- Active Quantheonix assistant
- Website hostname added to Allowed Domains

The frontend does not need:

- Gemini API keys
- JWT signing secrets
- database credentials
- user access tokens
- refresh tokens

Sensitive credentials remain on the backend.

## Installation

```bash
npm install @quantheonix/chatbot
```

## Usage

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

function App() {
  return (
    <>
      <main>
        <h1>My Website</h1>
      </main>

      <QuantheonixChat
        apiUrl="http://127.0.0.1:8000"
        assistantId="YOUR_ASSISTANT_ID"
      />
    </>
  );
}

export default App;
```

## Component API

| Prop | Type | Required | Description |
|---|---|---:|---|
| `apiUrl` | `string` | Yes | Base URL of the Quantheonix backend |
| `assistantId` | `string` | Yes | UUID of the assistant |

Example:

```jsx
<QuantheonixChat
  apiUrl="https://api.example.com"
  assistantId="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
/>
```

Widget styling and behavior are loaded automatically from the assistant configuration stored in Quantheonix.

## Architecture

```text
React Website
      |
      | @quantheonix/chatbot
      |
      v
Public Assistant Config
      |
      v
Chat Widget
      |
      v
Public Chat Stream
      |
      v
Quantheonix Backend
      |
      +----------------------+
      |                      |
      v                      v
PostgreSQL               AI Provider
```

## Public Configuration

The widget loads:

```http
GET /api/v1/public/assistants/{assistant_id}/config
```

This provides values such as:

- display name
- welcome message
- placeholder
- widget position
- colors
- font
- dimensions
- border radius
- launcher configuration
- feature toggles

These values do not need to be duplicated in the customer website.

## Public Chat

Messages are sent to:

```http
POST /api/v1/public/chat/stream
```

Example request:

```json
{
  "assistant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "conversation_id": null,
  "message": "Hello"
}
```

The backend responds with NDJSON events:

```json
{"type":"start","conversation_id":"..."}
{"type":"chunk","text":"Hello"}
{"type":"chunk","text":"! How can I help?"}
{"type":"done","conversation_id":"..."}
```

The package handles this stream automatically.

## Conversation Memory

The backend returns a `conversation_id` when a conversation starts.

The widget keeps that ID and includes it with later messages so the assistant can use previous conversation history.

Using **New chat** resets the conversation ID and starts a separate conversation.

## Allowed Domains

Before deploying the widget, add the website hostname to the assistant's **Allowed Domains** configuration.

Production example:

```text
example.com
```

Development example:

```text
localhost
```

Unauthorized origins are rejected by the backend.

## CORS

Allowed Domains and CORS are separate protections.

Allowed Domains decide which websites may use an assistant.

CORS decides which browser origins may read API responses.

For development you may need origins such as:

```text
http://localhost:5173
http://localhost:5174
```

Production deployments should use the real frontend origin.

## Environment Variables

With Vite:

```env
VITE_CHATBOT_API_URL=https://api.example.com
VITE_CHATBOT_ASSISTANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Then:

```jsx
<QuantheonixChat
  apiUrl={import.meta.env.VITE_CHATBOT_API_URL}
  assistantId={
    import.meta.env.VITE_CHATBOT_ASSISTANT_ID
  }
/>
```

The API URL and assistant ID are public identifiers, not secrets.

## Security

Never expose these values in frontend code:

- AI provider API keys
- JWT secret keys
- database passwords
- PostgreSQL connection strings
- access tokens
- refresh tokens
- private backend credentials

## Local Development

Start the backend:

```bash
uvicorn main:app --reload
```

Start the React application:

```bash
npm run dev
```

Make sure:

1. the assistant is active,
2. `localhost` exists in Allowed Domains,
3. the frontend origin is allowed by CORS,
4. the backend is reachable from the browser.

## React Support

The current package is intended for React applications.

Standalone plain-HTML `<script>` integration is not yet included.

## Self-Hosted Deployments

The `apiUrl` must be reachable from the user's browser.

For example:

```text
http://192.168.1.50:8000
```

A browser on another computer cannot use:

```text
http://127.0.0.1:8000
```

to reach your server because `127.0.0.1` refers to that browser's own device.

## Package Contents

```text
dist/
  quantheonix-chatbot.js
  chatbot.css

README.md
```

## License

MIT