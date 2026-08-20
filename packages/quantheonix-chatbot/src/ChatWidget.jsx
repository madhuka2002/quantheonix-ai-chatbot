import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import MarkdownMessage
  from "./MarkdownMessage";

import {
  streamPublicMessage,
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
  assistantId,
  title,
  settings,
}) {
  const welcomeMessage =
    settings.welcome_message ||
    "Hello! How can I help you?";

  const placeholder =
    settings.placeholder ||
    "Type your message...";

  const position =
    settings.position ||
    "bottom-right";

  const [isOpen, setIsOpen] =
    useState(
      Boolean(
        settings.initially_open,
      ),
    );

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

  const messagesRef =
    useRef(null);


  useEffect(() => {
    const element =
      messagesRef.current;

    if (!element) {
      return;
    }

    element.scrollTop =
      element.scrollHeight;
  }, [
    messages,
    isStreaming,
  ]);


  const widgetStyle =
    useMemo(
      () => ({
        "--qx-primary":
          settings.primary_color ||
          "#4f46e5",

        "--qx-secondary":
          settings.secondary_color ||
          "#64748b",

        "--qx-background":
          settings.background_color ||
          "#ffffff",

        "--qx-text":
          settings.text_color ||
          "#1e293b",

        "--qx-assistant-bubble":
          settings.assistant_bubble_color ||
          "#e2e8f0",

        "--qx-user-bubble":
          settings.user_bubble_color ||
          "#4f46e5",

        "--qx-font-family":
          settings.font_family ||
          "Inter",

        "--qx-font-size":
          `${settings.font_size || 14}px`,

        "--qx-widget-width":
          `${settings.widget_width || 380}px`,

        "--qx-widget-height":
          `${settings.widget_height || 620}px`,

        "--qx-border-radius":
          `${settings.border_radius || 16}px`,

        "--qx-launcher-size":
          `${settings.launcher_size || 58}px`,
      }),
      [settings],
    );


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
        await streamPublicMessage({
          apiUrl,
          assistantId,
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
        setMessages(
          (currentMessages) =>
            currentMessages.filter(
              (message) =>
                !(
                  message.id ===
                    assistantMessageId &&
                  !message.content
                ),
            ),
        );

        return;
      }

      setMessages(
        (currentMessages) =>
          currentMessages.filter(
            (message) =>
              !(
                message.id ===
                  assistantMessageId &&
                !message.content
              ),
          ),
      );

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


  function handleKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      if (
        input.trim() &&
        !isStreaming
      ) {
        event.currentTarget
          .form
          ?.requestSubmit();
      }
    }
  }


  return (
    <div
      className={
        `qx-widget qx-widget--${position}`
      }
      style={widgetStyle}
    >
      {isOpen && (
        <section className="qx-widget__panel">
          <header className="qx-widget__header">
            <div className="qx-widget__identity">
              {settings.avatar_url && (
                <img
                  className="qx-widget__avatar"
                  src={settings.avatar_url}
                  alt=""
                />
              )}

              <div>
                <strong>
                  {title}
                </strong>

                <span>
                  Online
                </span>
              </div>
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

          {settings.show_new_chat !==
            false && (
            <div className="qx-widget__toolbar">
              <button
                type="button"
                onClick={handleNewChat}
                disabled={isStreaming}
              >
                New chat
              </button>
            </div>
          )}

          <div
            ref={messagesRef}
            className="qx-widget__messages"
          >
            {messages.map(
              (message) => (
                <article
                  key={message.id}
                  className={
                    `qx-widget__message ` +
                    `qx-widget__message--${message.role}`
                  }
                >
                  {message.role ===
                  "assistant" ? (
                    <MarkdownMessage
                      content={
                        message.content ||
                        (
                          isStreaming
                            ? "..."
                            : ""
                        )
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
              onKeyDown={handleKeyDown}
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
                disabled={!input.trim()}
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
          {settings.launcher_icon ? (
            <img
              src={
                settings.launcher_icon
              }
              alt=""
            />
          ) : (
            "QX"
          )}
        </button>
      )}
    </div>
  );
}


export default ChatWidget;