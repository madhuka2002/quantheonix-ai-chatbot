function ChatHeader({
  conversationId,
  isLoading,
  isResetting,
  onNewChat,
}) {
  return (
    <header className="chat__header">
      <div className="chat__heading">
        <div>
          <h1>Quantheonix AI Assistant</h1>

          <p>
            {conversationId
              ? `Conversation: ${conversationId}`
              : "Start a new conversation"}
          </p>
        </div>

        <button
          className="chat__reset-button"
          type="button"
          onClick={onNewChat}
          disabled={isLoading || isResetting}
        >
          {isResetting ? "Resetting..." : "New Chat"}
        </button>
      </div>
    </header>
  );
}

export default ChatHeader;