import { useState } from "react";

import "./App.css";
import { sendChatMessage } from "./services/chatApi";


function App() {
  const [input, setInput] = useState("");

  const [messages, setMessages] = useState([
    {
      id: crypto.randomUUID(),
      role: "assistant",
      content:
        "Hello! I am the Quantheonix AI Assistant. How can I help you?",
    },
  ]);

  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");


  async function handleSubmit(event) {
    event.preventDefault();

    const userMessage = input.trim();

    if (!userMessage || isLoading) {
      return;
    }

    setError("");
    setInput("");

    const newUserMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: userMessage,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      newUserMessage,
    ]);

    setIsLoading(true);

    try {
      const data = await sendChatMessage(
        userMessage,
        conversationId,
      );

      setConversationId(data.conversation_id);

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.reply,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "An unexpected error occurred.",
      );
    } finally {
      setIsLoading(false);
    }
  }


  return (
    <main className="app">
      <section className="chat">
        <header className="chat__header">
          <div>
            <h1>Quantheonix AI Assistant</h1>
            <p>
              {conversationId
                ? `Conversation: ${conversationId}`
                : "Start a new conversation"}
            </p>
          </div>
        </header>

        <div
          className="chat__messages"
          aria-live="polite"
          aria-label="Chat messages"
        >
          {messages.map((message) => (
            <article
              className={`message message--${message.role}`}
              key={message.id}
            >
              <span className="message__sender">
                {message.role === "user"
                  ? "You"
                  : "Quantheonix"}
              </span>

              <p>{message.content}</p>
            </article>
          ))}

          {isLoading && (
            <article className="message message--assistant">
              <span className="message__sender">
                Quantheonix
              </span>

              <p>Thinking...</p>
            </article>
          )}
        </div>

        {error && (
          <p className="chat__error" role="alert">
            {error}
          </p>
        )}

        <form
          className="chat__form"
          onSubmit={handleSubmit}
        >
          <label
            className="sr-only"
            htmlFor="chat-message"
          >
            Enter your message
          </label>

          <input
            id="chat-message"
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Type your message..."
            maxLength={2000}
            disabled={isLoading}
            autoComplete="off"
          />

          <button
            type="submit"
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </form>
      </section>
    </main>
  );
}


export default App;