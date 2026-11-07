function ChatHeader({
  conversationId,
  assistantName,
  isLoading,
  isResetting,
  onNewChat,
  onOpenHistory,
}) {
  return (
    <header className="chat__header">
      <div className="chat__heading">
        <div>
          <span className="chat__eyebrow">
            Testing assistant
          </span>

          <h1>{assistantName}</h1>

          <p>
            {conversationId
              ? `Conversation: ${conversationId}`
              : "Start a new conversation"}
          </p>
        </div>

        <div className="chat__header-actions">
          <button
            className="chat__history-button"
            type="button"
            onClick={onOpenHistory}
          >
            History
          </button>

          <button
            className="chat__reset-button"
            type="button"
            onClick={onNewChat}
            disabled={isLoading || isResetting}
          >
            {isResetting ? "Resetting..." : "New chat"}
          </button>
        </div>
      </div>
    </header>
  );
}

export default ChatHeader;
