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
  } = useChat();

  const {
    conversations,
    isLoadingHistory,
    historyError,
    loadConversations,
    removeConversation,
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
    } catch (requestError) {
      console.error(
        "Conversation deletion failed:",
        requestError,
      );
    }
  }


  async function handleCreateNewChat() {
    await handleNewChat();
    await loadConversations();
  }


  return (
    <div className="chat-shell">
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={conversationId}
        isLoading={isLoadingHistory}
        error={historyError}
        user={user}
        onSelectConversation={openConversation}
        onDeleteConversation={
          handleDeleteFromSidebar
        }
        onNewChat={handleCreateNewChat}
        onRefresh={loadConversations}
        onLogout={logout}
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
          messagesEndRef={messagesEndRef}
        />

        <ChatInput
          input={input}
          isLoading={isLoading}
          textareaRef={textareaRef}
          onInputChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onSubmit={handleSubmit}
        />
      </div>
    </div>
  );
}


export default ChatApplication;