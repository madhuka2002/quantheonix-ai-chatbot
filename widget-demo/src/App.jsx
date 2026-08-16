import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

import "./App.css";


const API_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


async function refreshAccessToken() {
  const refreshToken =
    localStorage.getItem(
      "quantheonix_refresh_token",
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

  const data =
    await response.json();

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


function App() {
  async function getAccessToken({
    forceRefresh = false,
  } = {}) {
    console.log(
      "getAccessToken called:",
      forceRefresh,
    );

    if (!forceRefresh) {
      return localStorage.getItem(
        "quantheonix_access_token",
      );
    }

    console.log(
      "Token refresh requested by chatbot",
    );

    return refreshAccessToken();
  }


  return (
    <main className="demo-page">
      <section className="demo-content">
        <p className="demo-label">
          Package integration test
        </p>

        <h1>
          Quantheonix Chatbot Demo
        </h1>

        <p>
          This page tests the chatbot as an
          externally installed npm package.
        </p>
      </section>

      <QuantheonixChat
        apiUrl={API_URL}
        getAccessToken={getAccessToken}
        title="Quantheonix AI"
        welcomeMessage={
          "Hello! How can I help you today?"
        }
        placeholder="Ask something..."
        initiallyOpen
        position="bottom-right"
      />
    </main>
  );
}


export default App;