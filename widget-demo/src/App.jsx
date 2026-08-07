import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

import "./App.css";


function App() {
  const accessToken =
    localStorage.getItem(
      "quantheonix_access_token",
    )
    ?.trim() || null;

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
        apiUrl="http://127.0.0.1:8000"
        accessToken={accessToken}
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