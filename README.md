# Authentication

Quantheonix uses JWT-based authentication to protect chatbot conversations and ensure that conversations belong to the authenticated user.

The authentication system uses two tokens:

- **Access token** — sent with protected API requests.
- **Refresh token** — used to obtain a new access token when the current access token expires.

The host application is responsible for authenticating its users and providing a valid access token to the Quantheonix chatbot widget.

The widget itself does not require developers to manually copy tokens from Swagger, browser developer tools, or the console.

A normal application flow is:

```text
User
  |
  v
Register / Login
  |
  v
Quantheonix Backend
  |
  +---- access_token
  |
  +---- refresh_token
  |
  v
Host React Application
  |
  v
@quantheonix/chatbot
  |
  | Authorization: Bearer <access_token>
  v
Protected Chat API
```

---

## Authentication Endpoints

The Quantheonix backend provides the following authentication endpoints:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
```

The exact request and response schemas can also be inspected through the FastAPI API documentation when the backend is running.

---

## Register a User

A user must first have an account before using authenticated chatbot functionality.

Example request:

```http
POST /api/v1/auth/register
Content-Type: application/json
```

Send the registration fields required by the backend registration schema.

After registration, the user can log in through the login endpoint.

---

## Login

Authenticate the user through:

```http
POST /api/v1/auth/login
Content-Type: application/json
```

Example request:

```json
{
  "identifier": "user@example.com",
  "password": "your-password"
}
```

A successful login returns an authentication response containing values including:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_expires_in": 604800,
  "user": {
    "id": "...",
    "email": "user@example.com",
    "username": "example-user"
  }
}
```

The exact expiration values depend on the backend configuration.

The access token is used for authenticated API requests.

The refresh token is used to obtain a new token pair when the access token expires.

---

## Using an Access Token

For simple development or testing, an access token can be passed directly to the widget:

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

function App() {
  const accessToken =
    localStorage.getItem(
      "quantheonix_access_token"
    );

  return (
    <QuantheonixChat
      apiUrl="http://localhost:8000"
      accessToken={accessToken}
    />
  );
}

export default App;
```

Protected requests are sent using:

```http
Authorization: Bearer <access_token>
```

Passing a static `accessToken` is useful for development and testing.

For a real application, `getAccessToken` is recommended because it allows the widget to recover automatically when an access token expires.

---

# Token Refresh

Access tokens are intentionally short-lived.

A real client application should therefore support refresh tokens instead of requiring the user to manually obtain and paste a new access token.

Quantheonix supports this through the `getAccessToken` callback.

The widget can request the current token using:

```js
getAccessToken({
  forceRefresh: false
});
```

If an authenticated request receives `401 Unauthorized`, the widget can request a refreshed token using:

```js
getAccessToken({
  forceRefresh: true
});
```

The host application should then call the Quantheonix refresh endpoint and return the new access token.

---

## Recommended React Authentication Integration

The following is a basic integration example.

```jsx
import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

const API_URL =
  import.meta.env.VITE_CHATBOT_API_URL;

async function getAccessToken({
  forceRefresh = false,
} = {}) {
  if (!forceRefresh) {
    return localStorage.getItem(
      "quantheonix_access_token"
    );
  }

  const refreshToken =
    localStorage.getItem(
      "quantheonix_refresh_token"
    );

  if (!refreshToken) {
    return null;
  }

  const response = await fetch(
    `${API_URL}/api/v1/auth/refresh`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    }
  );

  if (!response.ok) {
    localStorage.removeItem(
      "quantheonix_access_token"
    );

    localStorage.removeItem(
      "quantheonix_refresh_token"
    );

    return null;
  }

  const data = await response.json();

  localStorage.setItem(
    "quantheonix_access_token",
    data.access_token
  );

  localStorage.setItem(
    "quantheonix_refresh_token",
    data.refresh_token
  );

  return data.access_token;
}

function App() {
  return (
    <QuantheonixChat
      apiUrl={API_URL}
      getAccessToken={getAccessToken}
      title="Quantheonix AI"
    />
  );
}

export default App;
```

This provides the widget with the current access token and allows it to request a new token when authentication expires.

---

## Example Login Integration

A host application can store the tokens after a successful login.

```js
const API_URL =
  import.meta.env.VITE_CHATBOT_API_URL;

async function login(
  identifier,
  password
) {
  const response = await fetch(
    `${API_URL}/api/v1/auth/login`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        identifier,
        password,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Login failed."
    );
  }

  const data = await response.json();

  localStorage.setItem(
    "quantheonix_access_token",
    data.access_token
  );

  localStorage.setItem(
    "quantheonix_refresh_token",
    data.refresh_token
  );

  return data.user;
}
```

A simple application flow can therefore be:

```text
Application starts
      |
      v
User logs in
      |
      v
POST /api/v1/auth/login
      |
      v
Access + Refresh Token
      |
      v
Tokens stored by host application
      |
      v
Chatbot receives access token
      |
      v
POST /api/v1/chat/stream
      |
      +---------------------------+
      |                           |
     200                         401
      |                           |
      v                           v
Continue chat             Refresh token
                                  |
                                  v
                       POST /api/v1/auth/refresh
                                  |
                                  v
                         New token pair
                                  |
                                  v
                           Retry request
```

---

## Refresh Endpoint

The refresh endpoint is:

```http
POST /api/v1/auth/refresh
Content-Type: application/json
```

The refresh token is sent in the JSON request body:

```json
{
  "refresh_token": "..."
}
```

A successful refresh returns a new authentication response containing a new access token and refresh token.

Applications should replace the previously stored token pair with the newly returned values.

---

## Why `getAccessToken` Is Recommended

Using:

```jsx
<QuantheonixChat
  accessToken={accessToken}
/>
```

is supported, but the supplied token may eventually expire.

Using:

```jsx
<QuantheonixChat
  getAccessToken={getAccessToken}
/>
```

allows the host application to provide fresh authentication credentials when required.

This is the recommended integration for authenticated applications.

---

## Important Security Note

The authentication examples above demonstrate the widget integration contract.

Production applications may choose a different browser-side token storage strategy depending on their security architecture.

Regardless of the storage strategy, never expose backend secrets in frontend code.

Do not place any of the following in React, Vite, Next.js, or other browser bundles:

```text
GEMINI_API_KEY
JWT_SECRET_KEY
POSTGRES_PASSWORD
DATABASE_URL
```

The browser only needs the user's authentication credentials required to communicate with the backend.

Gemini credentials, JWT signing secrets, database credentials, and other server secrets must remain on the backend.

---

## Authentication Responsibilities

The responsibilities are intentionally separated.

### Host Application

The host application is responsible for:

- displaying registration and login interfaces
- authenticating users
- storing or managing authentication state
- providing the access token to the chatbot
- refreshing authentication when necessary
- logging the user out when authentication can no longer be refreshed

### Quantheonix Widget

`@quantheonix/chatbot` is responsible for:

- requesting an access token from `getAccessToken`
- attaching the access token to protected chatbot requests
- detecting authentication failures
- requesting a refreshed token when supported
- retrying the appropriate request after successful token refresh

### Quantheonix Backend

The backend is responsible for:

- registering users
- authenticating credentials
- issuing access tokens
- issuing refresh tokens
- validating JWT access tokens
- validating refresh tokens
- issuing replacement token pairs
- enforcing conversation ownership
- protecting authenticated chatbot endpoints

This separation allows Quantheonix to integrate with a normal client application without requiring users to manually manage access tokens.