# @quantheonix/chatbot

Embeddable React AI chatbot widget for applications using the Quantheonix backend.

The package provides a reusable chatbot interface with streaming responses, Markdown rendering, syntax highlighting, authentication support, token refresh integration, and configurable presentation.

> `@quantheonix/chatbot` is the frontend client/widget only.  
> A running Quantheonix backend is required.

---

## Features

- React chatbot widget
- Streaming AI responses
- NDJSON stream handling
- Markdown rendering
- GitHub-flavored Markdown support
- Syntax-highlighted code blocks
- JWT access-token support
- Automatic retry after `401` through `getAccessToken`
- Token refresh integration
- Stop generation
- New chat
- Configurable title
- Configurable welcome message
- Configurable placeholder
- Open/closed initial state
- Bottom-right placement
- Bottom-left placement
- Responsive mobile layout
- Conversation ID support
- Error handling

---

## Requirements

The frontend application requires:

- React 18 or newer
- React DOM 18 or newer
- A running Quantheonix backend API

The npm package does **not** contain:

- Gemini API keys
- JWT signing secrets
- PostgreSQL credentials
- backend database logic

Those remain on the backend.

---

# Installation

Install the package:

```bash
npm install @quantheonix/chatbot
```

---

# Basic Usage

Import the component:

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";
```

Then use it in your React application:

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

The chatbot will connect to the Quantheonix backend provided through `apiUrl`.

---

# Backend Requirement

`@quantheonix/chatbot` is not a standalone AI service.

The package communicates with a compatible Quantheonix backend.

Architecture:

```text
React Application
       |
       | @quantheonix/chatbot
       |
       v
Quantheonix Backend
       |
       +--------------------+
       |                    |
       v                    v
PostgreSQL              Gemini API
```

The backend is responsible for:

- authentication
- access tokens
- refresh tokens
- conversations
- AI generation
- streaming
- PostgreSQL persistence
- Gemini API integration
- rate limiting
- CORS
- error handling

See:

```text
docs/backend-setup.md
```

for complete backend setup instructions.

---

# Configuration

The main component is:

```jsx
<QuantheonixChat />
```

Supported props:

| Prop | Type | Required | Default | Description |
|---|---|---:|---|---|
| `apiUrl` | `string` | Yes | — | Base URL of the Quantheonix backend |
| `accessToken` | `string \| null` | No | `null` | JWT access token |
| `getAccessToken` | `function \| null` | No | `null` | Callback used to obtain or refresh an access token |
| `title` | `string` | No | `"Quantheonix AI"` | Widget title |
| `welcomeMessage` | `string` | No | `"Hello! How can I help you?"` | Initial assistant message |
| `placeholder` | `string` | No | `"Type your message..."` | Input placeholder |
| `initiallyOpen` | `boolean` | No | `false` | Whether the widget starts open |
| `position` | `string` | No | `"bottom-right"` | Widget position |

---

# `apiUrl`

The `apiUrl` must point to the Quantheonix backend.

Local development example:

```jsx
<QuantheonixChat
  apiUrl="http://localhost:8000"
/>
```

Production example:

```jsx
<QuantheonixChat
  apiUrl="https://api.example.com"
/>
```

Do not point `apiUrl` directly to Gemini.

Do not place a Gemini API key in the frontend.

---

# Recommended Frontend Environment Variable

For Vite applications, the backend URL can be stored in a frontend environment variable:

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

Production:

```env
VITE_CHATBOT_API_URL=https://api.example.com
```

The backend URL is not a secret.

---

# Authentication

The package supports JWT-based authentication through either:

```text
accessToken
```

or:

```text
getAccessToken
```

---

## Fixed Access Token

If your application already has an access token:

```jsx
function App() {
  const accessToken =
    localStorage.getItem(
      "access_token",
    );

  return (
    <QuantheonixChat
      apiUrl="http://localhost:8000"
      accessToken={accessToken}
    />
  );
}
```

The package sends the token as:

```http
Authorization: Bearer ACCESS_TOKEN
```

---

# Recommended Authentication Integration

For applications that support token refresh, use:

```text
getAccessToken
```

Example:

```jsx
async function getAccessToken({
  forceRefresh = false,
} = {}) {
  if (!forceRefresh) {
    return localStorage.getItem(
      "quantheonix_access_token",
    );
  }

  const refreshToken =
    localStorage.getItem(
      "quantheonix_refresh_token",
    );

  if (!refreshToken) {
    return null;
  }

  const response = await fetch(
    "http://localhost:8000/api/v1/auth/refresh",
    {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    },
  );

  if (!response.ok) {
    localStorage.removeItem(
      "quantheonix_access_token",
    );

    localStorage.removeItem(
      "quantheonix_refresh_token",
    );

    return null;
  }

  const data = await response.json();

  localStorage.setItem(
    "quantheonix_access_token",
    data.access_token,
  );

  localStorage.setItem(
    "quantheonix_refresh_token",
    data.refresh_token,
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

---

# Automatic 401 Retry

When `getAccessToken` is provided, the package supports automatic recovery from an expired access token.

The request flow is:

```text
Chat request
     |
     v
401 Unauthorized
     |
     v
getAccessToken({
  forceRefresh: true
})
     |
     v
New access token
     |
     v
Retry chat request
```

If the refresh callback does not return a token, the chatbot reports an authentication error.

---

# `getAccessToken`

The callback receives:

```js
{
  forceRefresh: boolean
}
```

Normal request:

```js
forceRefresh === false
```

After a `401`:

```js
forceRefresh === true
```

Example:

```jsx
async function getAccessToken({
  forceRefresh,
}) {
  if (!forceRefresh) {
    return currentAccessToken;
  }

  return await refreshToken();
}
```

The host application remains responsible for implementing the actual authentication and refresh-token logic.

---

# Streaming Responses

The chatbot sends requests to:

```text
/api/v1/chat/stream
```

The backend returns:

```text
application/x-ndjson
```

The package consumes stream events such as:

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

The assistant response is displayed progressively as chunks arrive.

---

# Stop Generation

While a response is streaming, the widget displays a:

```text
Stop
```

button.

The current request is cancelled using:

```text
AbortController
```

This stops the active client-side streaming request.

---

# New Chat

The widget includes a:

```text
New chat
```

button.

Starting a new chat clears the widget's local message state and resets the current conversation ID.

The next message begins a new backend conversation.

---

# Conversation IDs

The package stores the conversation ID returned by the backend.

The flow is:

```text
First message
     |
     v
Backend creates conversation
     |
     v
conversation_id
     |
     v
Widget stores conversation ID
     |
     v
Later messages use same conversation
```

Selecting:

```text
New chat
```

resets the current conversation ID.

---

# Markdown Support

Assistant responses support Markdown.

Examples:

```markdown
# Heading

**Bold**

- List item
- Another item

`inline code`
```

The package also supports GitHub-flavored Markdown features.

---

# Code Highlighting

Assistant responses can include code blocks.

Example:

````markdown
```javascript
function hello() {
  console.log("Hello");
}
```