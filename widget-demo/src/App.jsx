import {
  QuantheonixChat,
} from "@quantheonix/chatbot";

import "@quantheonix/chatbot/chatbot.css";

import "./App.css";


const API_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

const ASSISTANT_ID =
  "78b036a3-a7dd-4722-8f1a-2011a44511e0";


function App() {
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

        <p>
          The chatbot configuration is loaded
          directly from the Quantheonix dashboard.
        </p>
      </section>

      <QuantheonixChat
        apiUrl={API_URL}
        assistantId={ASSISTANT_ID}
      />
    </main>
  );
}


export default App;