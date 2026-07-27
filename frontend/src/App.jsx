import {
  useEffect,
  useRef,
  useState,
} from "react";

import "./App.css";

import ChatHeader from "./components/ChatHeader";
import ChatInput from "./components/ChatInput";
import ErrorBanner from "./components/ErrorBanner";
import MessageList from "./components/MessageList";

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
        <ChatHeader
          conversationId={conversationId}
          isLoading={isLoading}
          isResetting={isResetting}
          onNewChat={handleNewChat}
        />

        <MessageList
          messages={messages}
          isLoading={isLoading}
          messagesEndRef={messagesEndRef}
        />

        <ErrorBanner
          error={error}
          failedMessage={failedMessage}
          isLoading={isLoading}
          onRetry={handleRetry}
        />

        <ChatInput
          input={input}
          isLoading={isLoading}
          isResetting={isResetting}
          textareaRef={textareaRef}
          onInputChange={(event) =>
            setInput(event.target.value)
          }
          onKeyDown={handleKeyDown}
          onSubmit={handleSubmit}
        />
      </section>
    </main>
  );
}


export default App;