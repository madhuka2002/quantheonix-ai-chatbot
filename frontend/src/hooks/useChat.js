import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  getConversation,
  sendChatMessage,
} from "../services/chatApi";

import {
  useAutoResizeTextarea,
} from "./useAutoResizeTextarea";

import {
  useLocalStorage,
} from "./useLocalStorage";


const STORAGE_KEYS = {
  conversationId:
    "quantheonix_conversation_id",
  messages:
    "quantheonix_chat_messages",
};


const WELCOME_MESSAGE = {
  id: "welcome-message",
  role: "assistant",
  content:
    "Hello! I am the Quantheonix AI Assistant. How can I help you?",
};


function createInitialMessages() {
  return [
    WELCOME_MESSAGE,
  ];
}


function isValidMessage(message) {
  return (
    message &&
    typeof message === "object" &&
    typeof message.id === "string" &&
    ["user", "assistant"].includes(
      message.role,
    ) &&
    typeof message.content === "string"
  );
}


function convertStoredMessages(
  storedMessages,
) {
  if (!Array.isArray(storedMessages)) {
    return createInitialMessages();
  }

  const restoredMessages =
    storedMessages
      .filter(isValidMessage)
      .map((message) => ({
        id: message.id,
        role: message.role,
        content: message.content,
        createdAt:
          message.created_at ??
          message.createdAt ??
          null,
      }));

  return [
    WELCOME_MESSAGE,
    ...restoredMessages,
  ];
}


export function useChat() {
  const [input, setInput] =
    useState("");

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

  const [
    isLoading,
    setIsLoading,
  ] = useState(false);

  const [
    isRestoring,
    setIsRestoring,
  ] = useState(
    () => Boolean(conversationId),
  );

  const [
    isResetting,
    setIsResetting,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  const [
    failedMessage,
    setFailedMessage,
  ] = useState(null);

  const messagesEndRef =
    useRef(null);

  const textareaRef =
    useRef(null);


  const safeMessages = useMemo(
    () => {
      if (
        Array.isArray(messages) &&
        messages.length > 0 &&
        messages.every(isValidMessage)
      ) {
        return messages;
      }

      return createInitialMessages();
    },
    [messages],
  );


  const isBusy =
    isLoading ||
    isRestoring ||
    isResetting;


  useAutoResizeTextarea(
    textareaRef,
    input,
    160,
  );


  function focusTextarea() {
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
    });
  }


  async function openConversation(
    selectedConversationId,
  ) {
    if (
      !selectedConversationId ||
      isBusy
    ) {
      return false;
    }

    if (
      selectedConversationId ===
      conversationId
    ) {
      focusTextarea();
      return true;
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

      return true;
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The conversation could not be loaded.",
      );

      return false;
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

        setMessages(
          restoredMessages,
        );
      } catch (requestError) {
        if (isCancelled) {
          return;
        }

        if (requestError?.status === 404) {
          removeStoredConversationId();
          removeStoredMessages();

          setConversationId(null);
          setMessages(
            createInitialMessages(),
          );

          setFailedMessage(null);
          setInput("");

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

    void restoreConversation();

    return () => {
      isCancelled = true;
    };
  }, [
    conversationId,
    removeStoredConversationId,
    removeStoredMessages,
    setConversationId,
    setMessages,
  ]);


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
      return false;
    }

    setError("");
    setFailedMessage(null);
    setInput("");

    if (addUserMessage) {
      const userMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: cleanedMessage,
        createdAt:
          new Date().toISOString(),
      };

      setMessages(
        (currentMessages) => [
          ...currentMessages,
          userMessage,
        ],
      );
    }

    setIsLoading(true);

    try {
      const response =
        await sendChatMessage(
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
        createdAt:
          new Date().toISOString(),
      };

      setMessages(
        (currentMessages) => [
          ...currentMessages,
          assistantMessage,
        ],
      );

      return {
        conversationId:
          response.conversation_id,
        reply: response.reply,
      };
    } catch (requestError) {
      setFailedMessage(
        cleanedMessage,
      );

      setError(
        requestError instanceof Error
          ? requestError.message
          : "An unexpected error occurred.",
      );

      return false;
    } finally {
      setIsLoading(false);
      focusTextarea();
    }
  }


  async function handleSubmit(event) {
    event?.preventDefault?.();

    return submitMessage(input);
  }


  function handleInputChange(event) {
    setInput(
      event.target.value,
    );
  }


  async function handleKeyDown(event) {
    const isComposing =
      event.nativeEvent?.isComposing;

    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !isComposing
    ) {
      event.preventDefault();

      return submitMessage(input);
    }

    return false;
  }


  async function handleRetry() {
    if (
      !failedMessage ||
      isBusy
    ) {
      return false;
    }

    const messageToRetry =
      failedMessage;

    setFailedMessage(null);
    setError("");

    return submitMessage(
      messageToRetry,
      {
        addUserMessage: false,
      },
    );
  }


  async function handleNewChat() {
    if (isBusy) {
      return false;
    }

    setError("");
    setFailedMessage(null);
    setIsResetting(true);

    try {
      /*
       * Starting a new chat must not delete the old
       * conversation from PostgreSQL. The sidebar's
       * delete button handles permanent deletion.
       */

      removeStoredConversationId();
      removeStoredMessages();

      setConversationId(null);
      setMessages(
        createInitialMessages(),
      );

      setInput("");

      return true;
    } finally {
      setIsResetting(false);
      focusTextarea();
    }
  }


  return {
    input,
    messages: safeMessages,
    conversationId,

    isLoading:
      isLoading ||
      isRestoring,

    isBusy,
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