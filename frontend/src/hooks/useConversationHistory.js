import {
  useCallback,
  useEffect,
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
  const [conversations, setConversations] =
    useState([]);

  const [search, setSearch] =
    useState("");

  const [
    isLoadingHistory,
    setIsLoadingHistory,
  ] = useState(true);

  const [historyError, setHistoryError] =
    useState("");


  const loadConversations = useCallback(
    async (searchValue = "") => {
      setIsLoadingHistory(true);
      setHistoryError("");

      try {
        const data = await listConversations({
          limit: 50,
          offset: 0,
          search: searchValue,
        });

        setConversations(
          normaliseConversations(data),
        );

        return data;
      } catch (error) {
        setHistoryError(
          error instanceof Error
            ? error.message
            : "Conversation history could not be loaded.",
        );

        return null;
      } finally {
        setIsLoadingHistory(false);
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
              conversation.id !== conversationId,
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
    let isCancelled = false;

    async function loadInitialHistory() {
      try {
        const data = await listConversations({
          limit: 50,
          offset: 0,
          search: "",
        });

        if (!isCancelled) {
          setConversations(
            normaliseConversations(data),
          );
        }
      } catch (error) {
        if (!isCancelled) {
          setHistoryError(
            error instanceof Error
              ? error.message
              : "Conversation history could not be loaded.",
          );
        }
      } finally {
        if (!isCancelled) {
          setIsLoadingHistory(false);
        }
      }
    }

    void loadInitialHistory();

    return () => {
      isCancelled = true;
    };
  }, []);


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