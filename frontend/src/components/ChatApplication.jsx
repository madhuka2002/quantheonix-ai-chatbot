import "../App.css";

import ChatHeader from "./ChatHeader";
import ChatInput from "./ChatInput";
import ErrorBanner from "./ErrorBanner";
import MessageList from "./MessageList";

import { useChat } from "../hooks/useChat";



function ChatApplication() {
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
  } = useChat();


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
          onInputChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onSubmit={handleSubmit}
        />
      </section>
    </main>
  );
}


export default ChatApplication;