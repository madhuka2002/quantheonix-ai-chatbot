import "../App.css";

import ChatHeader from "./ChatHeader";
import ChatInput from "./ChatInput";
import ConversationSidebar from "./ConversationSidebar";
import ErrorBanner from "./ErrorBanner";
import MessageList from "./MessageList";

import { useAuth } from "../hooks/useAuth";
import { useChat } from "../hooks/useChat";
import {
  useConversationHistory,
} from "../hooks/useConversationHistory";


function ChatApplication() {
  const {
    user,
    logout,
  } = useAuth();

  const {
    input,
    messages,
    conversationId,
    isLoading,
    isStreaming,
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
    handleStopGeneration,
    handleEditUserMessage,
    handleRegenerateResponse,
    openConversation,
  } = useChat();

  const {
    conversations,
    search,
    setSearch,
    isLoadingHistory,
    historyError,
    loadConversations,
    removeConversation,
    updateConversationTitle,
  } = useConversationHistory();


  async function handleDeleteFromSidebar(
    selectedConversationId,
  ) {
    const shouldDelete = window.confirm(
      "Delete this conversation permanently?",
    );

    if (!shouldDelete) {
      return;
    }

    try {
      await removeConversation(
        selectedConversationId,
      );

      if (
        selectedConversationId ===
        conversationId
      ) {
        await handleNewChat();
      }

      await loadConversations(search);
    } catch (requestError) {
      console.error(
        "Conversation deletion failed:",
        requestError,
      );
    }
  }


  async function handleCreateNewChat() {
    try {
      await handleNewChat();
      await loadConversations(search);
    } catch (requestError) {
      console.error(
        "New chat creation failed:",
        requestError,
      );
    }
  }


  async function handleRenameConversation(
    selectedConversationId,
    title,
  ) {
    try {
      await updateConversationTitle(
        selectedConversationId,
        title,
      );
    } catch (requestError) {
      console.error(
        "Conversation rename failed:",
        requestError,
      );
    }
  }


  async function handleChatSubmit(event) {
    try {
      const result = await handleSubmit(event);

      if (
        result?.conversationId &&
        !result?.aborted
      ) {
        await loadConversations(search);
      }

      return result;
    } catch (requestError) {
      console.error(
        "Chat submission failed:",
        requestError,
      );

      return false;
    }
  }


  async function handleChatKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.nativeEvent?.isComposing
    ) {
      event.preventDefault();

      await handleChatSubmit(event);

      return;
    }

    await handleKeyDown(event);
  }


  async function handleConversationSelection(
    selectedConversationId,
  ) {
    if (
      !selectedConversationId ||
      selectedConversationId ===
        conversationId
    ) {
      return;
    }

    try {
      await openConversation(
        selectedConversationId,
      );
    } catch (requestError) {
      console.error(
        "Conversation loading failed:",
        requestError,
      );
    }
  }


  async function handleEditMessage(
    messageId,
    editedContent,
  ) {
    try {
      const result =
        await handleEditUserMessage(
          messageId,
          editedContent,
        );

      if (
        result?.conversationId &&
        !result?.aborted
      ) {
        await loadConversations(search);
      }

      return result;
    } catch (requestError) {
      console.error(
        "Message editing failed:",
        requestError,
      );

      return false;
    }
  }


  async function handleRegenerate() {
    try {
      const result =
        await handleRegenerateResponse();

      if (
        result?.conversationId &&
        !result?.aborted
      ) {
        await loadConversations(search);
      }

      return result;
    } catch (requestError) {
      console.error(
        "Response regeneration failed:",
        requestError,
      );

      return false;
    }
  }


  function handleLogout() {
    logout();
  }


  return (
    <div className="chat-shell">
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={conversationId}
        isLoading={isLoadingHistory}
        error={historyError}
        user={user}
        search={search}
        onSearchChange={setSearch}
        onSelectConversation={
          handleConversationSelection
        }
        onDeleteConversation={
          handleDeleteFromSidebar
        }
        onRenameConversation={
          handleRenameConversation
        }
        onNewChat={handleCreateNewChat}
        onRefresh={() =>
          loadConversations(search)
        }
        onLogout={handleLogout}
      />

      <div className="chat-main">
        <ChatHeader
          onNewChat={handleCreateNewChat}
          isResetting={isResetting}
        />

        <ErrorBanner
          error={error}
          failedMessage={failedMessage}
          onRetry={handleRetry}
        />

        <MessageList
          messages={messages}
          isLoading={isLoading}
          isStreaming={isStreaming}
          messagesEndRef={messagesEndRef}
          onRegenerate={handleRegenerate}
          onEditUserMessage={
            handleEditMessage
          }
        />

        <ChatInput
          input={input}
          isLoading={isLoading}
          isStreaming={isStreaming}
          isResetting={isResetting}
          textareaRef={textareaRef}
          onInputChange={handleInputChange}
          onKeyDown={handleChatKeyDown}
          onSubmit={handleChatSubmit}
          onStop={handleStopGeneration}
        />
      </div>
    </div>
  );
}


export default ChatApplication;