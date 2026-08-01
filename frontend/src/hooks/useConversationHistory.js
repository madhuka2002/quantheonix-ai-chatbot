import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  listConversations,
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

  const [
    isLoadingHistory,
    setIsLoadingHistory,
  ] = useState(true);

  const [historyError, setHistoryError] =
    useState("");


  const loadConversations = useCallback(
    async () => {
      setIsLoadingHistory(true);
      setHistoryError("");

      try {
        const data = await listConversations({
          limit: 50,
          offset: 0,
        });

        setConversations(
          normaliseConversations(data),
        );
      } catch (error) {
        setHistoryError(
          error instanceof Error
            ? error.message
            : "Conversation history could not be loaded.",
        );
      } finally {
        setIsLoadingHistory(false);
      }
    },
    [],
  );


  const removeConversation = useCallback(
    async (conversationId) => {
      if (!conversationId) {
        return;
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
    },
    [],
  );


  const addOrUpdateConversation =
    useCallback((conversation) => {
      if (!conversation?.id) {
        return;
      }

      setConversations(
        (currentConversations) => {
          const remaining =
            currentConversations.filter(
              (item) =>
                item.id !== conversation.id,
            );

          return [
            conversation,
            ...remaining,
          ];
        },
      );
    }, []);


  useEffect(() => {
    let isCancelled = false;

    async function restoreConversationHistory() {
      try {
        const data = await listConversations({
          limit: 50,
          offset: 0,
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

    void restoreConversationHistory();

    return () => {
      isCancelled = true;
    };
  }, []);


  return {
    conversations,
    isLoadingHistory,
    historyError,
    loadConversations,
    removeConversation,
    addOrUpdateConversation,
  };
}