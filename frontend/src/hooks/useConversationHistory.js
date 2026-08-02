import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  listConversations,
  renameConversation,
  resetConversation,
} from "../services/chatApi";


function normaliseConversations(data) {
  return Array.isArray(data?.conversations)
    ? data.conversations
    : [];
}


export function useConversationHistory() {
  const [
    conversations,
    setConversations,
  ] = useState([]);

  const [search, setSearch] =
    useState("");

  const [
    isLoadingHistory,
    setIsLoadingHistory,
  ] = useState(true);

  const [
    historyError,
    setHistoryError,
  ] = useState("");

  const latestRequestIdRef =
    useRef(0);


  const loadConversations = useCallback(
    async (searchValue = "") => {
      const requestId =
        latestRequestIdRef.current + 1;

      latestRequestIdRef.current =
        requestId;

      setIsLoadingHistory(true);
      setHistoryError("");

      try {
        const data =
          await listConversations({
            limit: 50,
            offset: 0,
            search: searchValue,
          });

        if (
          requestId !==
          latestRequestIdRef.current
        ) {
          return null;
        }

        setConversations(
          normaliseConversations(data),
        );

        return data;
      } catch (error) {
        if (
          requestId !==
          latestRequestIdRef.current
        ) {
          return null;
        }

        setHistoryError(
          error instanceof Error
            ? error.message
            : "Conversation history could not be loaded.",
        );

        return null;
      } finally {
        if (
          requestId ===
          latestRequestIdRef.current
        ) {
          setIsLoadingHistory(false);
        }
      }
    },
    [],
  );


  const removeConversation = useCallback(
    async (conversationId) => {
      if (!conversationId) {
        return false;
      }

      await resetConversation(
        conversationId,
      );

      setConversations(
        (currentConversations) =>
          currentConversations.filter(
            (conversation) =>
              conversation.id !==
              conversationId,
          ),
      );

      return true;
    },
    [],
  );


  const updateConversationTitle =
    useCallback(
      async (
        conversationId,
        title,
      ) => {
        const cleanedTitle =
          title.trim();

        if (
          !conversationId ||
          !cleanedTitle
        ) {
          return null;
        }

        const updatedConversation =
          await renameConversation(
            conversationId,
            cleanedTitle,
          );

        setConversations(
          (currentConversations) =>
            currentConversations.map(
              (conversation) =>
                conversation.id ===
                conversationId
                  ? {
                      ...conversation,
                      title:
                        updatedConversation.title,
                    }
                  : conversation,
            ),
        );

        return updatedConversation;
      },
      [],
    );


  useEffect(() => {
    const timeoutId =
      window.setTimeout(() => {
        void loadConversations(search);
      }, 300);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [
    search,
    loadConversations,
  ]);


  return {
    conversations,
    search,
    setSearch,
    isLoadingHistory,
    historyError,
    loadConversations,
    removeConversation,
    updateConversationTitle,
  };
}