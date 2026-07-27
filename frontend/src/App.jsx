import {
  useEffect,
  useRef,
  useState,
} from "react";

import "./App.css";

import {
  resetConversation,
  sendChatMessage,
} from "./services/chatApi";


const STORAGE_KEYS = {
  conversationId: "quantheonix_conversation_id",
  messages: "quantheonix_chat_messages",
};


const WELCOME_MESSAGE = {
  id: "welcome-message",
  role: "assistant",
  content:
    "Hello! I am the Quantheonix AI Assistant. How can I help you?",
};


function loadStoredMessages() {
  try {
    const storedMessages = localStorage.getItem(
      STORAGE_KEYS.messages,
    );

    if (!storedMessages) {
      return [WELCOME_MESSAGE];
    }

    const parsedMessages = JSON.parse(storedMessages);

    if (
      !Array.isArray(parsedMessages) ||
      parsedMessages.length === 0
    ) {
      return [WELCOME_MESSAGE];
    }

    return parsedMessages;
  } catch {
    return [WELCOME_MESSAGE];
  }
}


function App() {
  const [input, setInput] = useState("");

  const [messages, setMessages] = useState(
    loadStoredMessages,
  );

  const [conversationId, setConversationId] =
    useState(
      () =>
        localStorage.getItem(
          STORAGE_KEYS.conversationId,
        ) || null,
    );

  const [isLoading, setIsLoading] = useState(false);
  const [isResetting, setIsResetting] =
    useState(false);

  const [error, setError] = useState("");
  const [failedMessage, setFailedMessage] =
    useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);


  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEYS.messages,
      JSON.stringify(messages),
    );
  }, [messages]);


  useEffect(() => {
    if (conversationId) {
      localStorage.setItem(
        STORAGE_KEYS.conversationId,
        conversationId,
      );
    } else {
      localStorage.removeItem(
        STORAGE_KEYS.conversationId,
      );
    }
  }, [conversationId]);


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading, error]);


  useEffect(() => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";

    const maximumHeight = 160;

    textarea.style.height = `${Math.min(
      textarea.scrollHeight,
      maximumHeight,
    )}px`;
  }, [input]);


  async function submitMessage(messageText) {
    const cleanedMessage = messageText.trim();

    if (
      !cleanedMessage ||
      isLoading ||
      isResetting
    ) {
      return;
    }

    setError("");
    setFailedMessage(null);
    setInput("");

    const newUserMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: cleanedMessage,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      newUserMessage,
    ]);

    setIsLoading(true);

    try {
      const data = await sendChatMessage(
        cleanedMessage,
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
      setFailedMessage(cleanedMessage);

      setError(
        requestError instanceof Error
          ? requestError.message
          : "An unexpected error occurred.",
      );
    } finally {
      setIsLoading(false);

      requestAnimationFrame(() => {
        textareaRef.current?.focus();
      });
    }
  }


  async function handleSubmit(event) {
    event.preventDefault();

    await submitMessage(input);
  }


  function handleKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      submitMessage(input);
    }
  }


  async function handleRetry() {
    if (!failedMessage) {
      return;
    }

    const messageToRetry = failedMessage;

    setFailedMessage(null);
    setError("");

    await submitMessage(messageToRetry);
  }


  async function handleNewChat() {
    if (isLoading || isResetting) {
      return;
    }

    setError("");
    setFailedMessage(null);
    setIsResetting(true);

    try {
      if (conversationId) {
        await resetConversation(conversationId);
      }

      setConversationId(null);
      setMessages([WELCOME_MESSAGE]);
      setInput("");

      localStorage.removeItem(
        STORAGE_KEYS.conversationId,
      );

      localStorage.removeItem(
        STORAGE_KEYS.messages,
      );

      requestAnimationFrame(() => {
        textareaRef.current?.focus();
      });
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The conversation could not be reset.",
      );
    } finally {
      setIsResetting(false);
    }
  }


  return (
    <main className="app">
      <section className="chat">
        <header className="chat__header">
          <div className="chat__heading">
            <div>
              <h1>Quantheonix AI Assistant</h1>

              <p>
                {conversationId
                  ? `Conversation: ${conversationId}`
                  : "Start a new conversation"}
              </p>
            </div>

            <button
              className="chat__reset-button"
              type="button"
              onClick={handleNewChat}
              disabled={isLoading || isResetting}
            >
              {isResetting
                ? "Resetting..."
                : "New Chat"}
            </button>
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
            <article
              className="message message--assistant"
              aria-label="Quantheonix is typing"
            >
              <span className="message__sender">
                Quantheonix
              </span>

              <div className="typing-indicator">
                <span />
                <span />
                <span />
              </div>
            </article>
          )}

          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div
            className="chat__error"
            role="alert"
          >
            <p>{error}</p>

            {failedMessage && (
              <button
                type="button"
                onClick={handleRetry}
                disabled={isLoading}
              >
                Retry
              </button>
            )}
          </div>
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

          <textarea
            ref={textareaRef}
            id="chat-message"
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            maxLength={2000}
            rows={1}
            disabled={isLoading || isResetting}
            autoComplete="off"
          />

          <button
            type="submit"
            disabled={
              !input.trim() ||
              isLoading ||
              isResetting
            }
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </form>

        <p className="chat__hint">
          Press Enter to send. Use Shift + Enter for
          a new line.
        </p>
      </section>
    </main>
  );
}


export default App;