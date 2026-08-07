import {
  useRef,
  useState,
} from "react";

import MarkdownMessage
  from "./MarkdownMessage";

import {
  streamWidgetMessage,
} from "./chatApi";


function createMessage(
  role,
  content,
) {
  return {
    id: crypto.randomUUID(),
    role,
    content,
  };
}


function ChatWidget({
  apiUrl,
  accessToken,
  getAccessToken,
  title,
  welcomeMessage,
  placeholder,
  initiallyOpen,
  position,
}) {
  const [isOpen, setIsOpen] =
    useState(initiallyOpen);

  const [messages, setMessages] =
    useState([
      createMessage(
        "assistant",
        welcomeMessage,
      ),
    ]);

  const [input, setInput] =
    useState("");

  const [
    conversationId,
    setConversationId,
  ] = useState(null);

  const [isStreaming, setIsStreaming] =
    useState(false);

  const [error, setError] =
    useState("");

  const abortControllerRef =
    useRef(null);


  async function handleSubmit(event) {
    event.preventDefault();

    const cleanedMessage =
      input.trim();

    if (
      !cleanedMessage ||
      isStreaming
    ) {
      return;
    }

    const assistantMessageId =
      crypto.randomUUID();

    setMessages(
      (currentMessages) => [
        ...currentMessages,
        createMessage(
          "user",
          cleanedMessage,
        ),
        {
          id: assistantMessageId,
          role: "assistant",
          content: "",
        },
      ],
    );

    setInput("");
    setError("");
    setIsStreaming(true);

    const abortController =
      new AbortController();

    abortControllerRef.current =
      abortController;

    try {
      const result =
        await streamWidgetMessage({
          apiUrl,
          accessToken,
          getAccessToken,
          message: cleanedMessage,
          conversationId,
          signal:
            abortController.signal,

          onStart(eventData) {
            if (
              eventData.conversation_id
            ) {
              setConversationId(
                eventData.conversation_id,
              );
            }
          },

          onChunk(text) {
            setMessages(
              (currentMessages) =>
                currentMessages.map(
                  (message) =>
                    message.id ===
                    assistantMessageId
                      ? {
                          ...message,
                          content:
                            message.content +
                            text,
                        }
                      : message,
                ),
            );
          },

          onDone(eventData) {
            if (
              eventData.conversation_id
            ) {
              setConversationId(
                eventData.conversation_id,
              );
            }
          },
        });

      if (result.conversationId) {
        setConversationId(
          result.conversationId,
        );
      }
    } catch (requestError) {
      if (
        requestError?.name ===
        "AbortError"
      ) {
        return;
      }

      setError(
        requestError instanceof Error
          ? requestError.message
          : "The chatbot request failed.",
      );
    } finally {
      abortControllerRef.current =
        null;

      setIsStreaming(false);
    }
  }


  function handleStop() {
    abortControllerRef.current?.abort();
  }


  function handleNewChat() {
    if (isStreaming) {
      return;
    }

    setConversationId(null);

    setMessages([
      createMessage(
        "assistant",
        welcomeMessage,
      ),
    ]);

    setInput("");
    setError("");
  }


  return (
    <div
      className={
        `qx-widget qx-widget--${position}`
      }
    >
      {isOpen && (
        <section className="qx-widget__panel">
          <header className="qx-widget__header">
            <div>
              <strong>{title}</strong>
              <span>Online</span>
            </div>

            <button
              type="button"
              onClick={() =>
                setIsOpen(false)
              }
              aria-label="Close chatbot"
            >
              ×
            </button>
          </header>

          <div className="qx-widget__toolbar">
            <button
              type="button"
              onClick={handleNewChat}
              disabled={isStreaming}
            >
              New chat
            </button>
          </div>

          <div className="qx-widget__messages">
            {messages.map(
              (message) => (
                <article
                  key={message.id}
                  className={
                    `qx-widget__message qx-widget__message--${message.role}`
                  }
                >
                  {message.role ===
                  "assistant" ? (
                    <MarkdownMessage
                      content={
                        message.content
                      }
                    />
                  ) : (
                    <p>
                      {message.content}
                    </p>
                  )}
                </article>
              ),
            )}
          </div>

          {error && (
            <p className="qx-widget__error">
              {error}
            </p>
          )}

          <form
            className="qx-widget__form"
            onSubmit={handleSubmit}
          >
            <textarea
              value={input}
              onChange={(event) =>
                setInput(
                  event.target.value,
                )
              }
              placeholder={placeholder}
              disabled={isStreaming}
              rows={2}
            />

            {isStreaming ? (
              <button
                type="button"
                onClick={handleStop}
              >
                Stop
              </button>
            ) : (
              <button
                type="submit"
                disabled={
                  !input.trim()
                }
              >
                Send
              </button>
            )}
          </form>
        </section>
      )}

      {!isOpen && (
        <button
          className="qx-widget__launcher"
          type="button"
          onClick={() =>
            setIsOpen(true)
          }
          aria-label="Open chatbot"
        >
          QX
        </button>
      )}
    </div>
  );
}


export default ChatWidget;