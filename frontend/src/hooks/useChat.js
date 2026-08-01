import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  getConversation,
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


function convertStoredMessages(
  storedMessages,
) {
  if (!Array.isArray(storedMessages)) {
    return createInitialMessages();
  }

  const restoredMessages = storedMessages
    .filter((message) => {
      return (
        message &&
        typeof message.id === "string" &&
        ["user", "assistant"].includes(
          message.role,
        ) &&
        typeof message.content === "string"
      );
    })
    .map((message) => ({
      id: message.id,
      role: message.role,
      content: message.content,
      createdAt: message.created_at ?? null,
    }));

  return [
    WELCOME_MESSAGE,
    ...restoredMessages,
  ];
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

  const [isRestoring, setIsRestoring] =
    useState(Boolean(conversationId));

  const [isResetting, setIsResetting] =
    useState(false);

  const [error, setError] = useState("");

  const [failedMessage, setFailedMessage] =
    useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const hasRestoredConversationRef =
    useRef(false);


  const safeMessages =
    Array.isArray(messages) &&
    messages.length > 0 &&
    messages.every(isValidMessage)
      ? messages
      : createInitialMessages();


  const isBusy =
    isLoading ||
    isRestoring ||
    isResetting;


  useAutoResizeTextarea(
    textareaRef,
    input,
    160,
  );


  async function openConversation(
    selectedConversationId,
  ) {
    if (
      !selectedConversationId ||
      isBusy
    ) {
      return;
    }

    setError("");
    setFailedMessage(null);
    setIsRestoring(true);

    try {
      const conversation =
        await getConversation(
          selectedConversationId,
        );

      const restoredMessages =
        convertStoredMessages(
          conversation.messages,
        );

      setConversationId(
        selectedConversationId,
      );

      setMessages(
        restoredMessages,
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The conversation could not be loaded.",
      );
    } finally {
      setIsRestoring(false);
      focusTextarea();
    }
  }


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [
    safeMessages,
    isLoading,
    isRestoring,
    error,
  ]);


  useEffect(() => {
    if (hasRestoredConversationRef.current) {
      return undefined;
    }

    hasRestoredConversationRef.current = true;

    if (!conversationId) {
      return undefined;
    }

    let isCancelled = false;

    async function restoreConversation() {
      try {
        const conversation =
          await getConversation(
            conversationId,
          );

        if (isCancelled) {
          return;
        }

        const restoredMessages =
          convertStoredMessages(
            conversation.messages,
          );

        setMessages(restoredMessages);
      } catch (requestError) {
        if (isCancelled) {
          return;
        }

        if (requestError?.status === 404) {
          removeStoredConversationId();
          removeStoredMessages();

          setError(
            "The previous conversation no longer exists. A new chat has been started.",
          );

          return;
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : "The conversation could not be restored.",
        );
      } finally {
        if (!isCancelled) {
          setIsRestoring(false);
        }
      }
    }

    restoreConversation();

    return () => {
      isCancelled = true;
    };
  }, [
    conversationId,
    removeStoredConversationId,
    removeStoredMessages,
    setMessages,
  ]);


  function focusTextarea() {
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
    });
  }


  async function submitMessage(
    messageText,
    options = {},
  ) {
    const cleanedMessage =
      messageText.trim();

    const {
      addUserMessage = true,
    } = options;

    if (
      !cleanedMessage ||
      isBusy
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
    if (!failedMessage || isBusy) {
      return;
    }

    const messageToRetry =
      failedMessage;

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
    if (isBusy) {
      return;
    }

    setError("");
    setFailedMessage(null);
    setIsResetting(true);

    try {
      if (conversationId) {
        await resetConversation(
          conversationId,
        );
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
    isLoading:
      isLoading || isRestoring,
    isRestoring,
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
    openConversation,
  };
}