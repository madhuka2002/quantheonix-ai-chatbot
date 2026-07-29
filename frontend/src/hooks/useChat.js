import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  resetConversation,
  sendChatMessage,
} from "../services/chatApi";

import { useAutoResizeTextarea } from "./useAutoResizeTextarea";
import { useLocalStorage } from "./useLocalStorage";


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


function createInitialMessages() {
  return [WELCOME_MESSAGE];
}


function isValidMessage(message) {
  return (
    message &&
    typeof message === "object" &&
    typeof message.id === "string" &&
    ["user", "assistant"].includes(message.role) &&
    typeof message.content === "string"
  );
}


export function useChat() {
  const [input, setInput] = useState("");

  const [
    messages,
    setMessages,
    removeStoredMessages,
  ] = useLocalStorage(
    STORAGE_KEYS.messages,
    createInitialMessages,
  );

  const [
    conversationId,
    setConversationId,
    removeStoredConversationId,
  ] = useLocalStorage(
    STORAGE_KEYS.conversationId,
    null,
  );

  const [isLoading, setIsLoading] =
    useState(false);

  const [isResetting, setIsResetting] =
    useState(false);

  const [error, setError] = useState("");

  const [failedMessage, setFailedMessage] =
    useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);


  const safeMessages =
    Array.isArray(messages) &&
    messages.length > 0 &&
    messages.every(isValidMessage)
      ? messages
      : createInitialMessages();


  useAutoResizeTextarea(
    textareaRef,
    input,
    160,
  );


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [safeMessages, isLoading, error]);


  function focusTextarea() {
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
    });
  }


  async function submitMessage(
    messageText,
    options = {},
  ) {
    const cleanedMessage = messageText.trim();

    const {
      addUserMessage = true,
    } = options;

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

    if (addUserMessage) {
      const userMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: cleanedMessage,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        userMessage,
      ]);
    }

    setIsLoading(true);

    try {
      const response = await sendChatMessage(
        cleanedMessage,
        conversationId,
      );

      setConversationId(
        response.conversation_id,
      );

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.reply,
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
      focusTextarea();
    }
  }


  async function handleSubmit(event) {
    event.preventDefault();

    await submitMessage(input);
  }


  function handleInputChange(event) {
    setInput(event.target.value);
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

    await submitMessage(
      messageToRetry,
      {
        addUserMessage: false,
      },
    );
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
    } catch (requestError) {
      console.error(
        "The stored conversation could not be deleted:",
        requestError,
      );
    } finally {
      removeStoredConversationId();
      removeStoredMessages();
      setInput("");
      setIsResetting(false);
      focusTextarea();
    }
  }


  return {
    input,
    messages: safeMessages,
    conversationId,
    isLoading,
    isResetting,
    error,
    failedMessage,
    messagesEndRef,
    textareaRef,
    handleInputChange,
    handleKeyDown,
    handleSubmit,
    handleRetry,
    handleNewChat,
  };
}