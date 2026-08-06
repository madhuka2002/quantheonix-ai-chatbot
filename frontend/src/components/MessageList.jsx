import MessageBubble from "./MessageBubble";


function MessageList({
  messages,
  isLoading,
  isStreaming,
  messagesEndRef,
  onRegenerate,
  onEditUserMessage,
}) {
  const safeMessages =
    Array.isArray(messages)
      ? messages.filter(Boolean)
      : [];

  const latestAssistantId = [
    ...safeMessages,
  ]
    .reverse()
    .find(
      (message) =>
        message.role === "assistant" &&
        message.id !== "welcome-message",
    )?.id;

  return (
    <div
      className="chat__messages"
      aria-live="polite"
      aria-label="Chat messages"
      aria-busy={isLoading}
    >
      {safeMessages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          canRegenerate={
            message.id ===
            latestAssistantId
          }
          canEdit={
            message.role === "user"
          }
          isStreaming={isStreaming}
          onRegenerate={onRegenerate}
          onEdit={onEditUserMessage}
        />
      ))}

      <div
        ref={messagesEndRef}
        aria-hidden="true"
      />
    </div>
  );
}


export default MessageList;