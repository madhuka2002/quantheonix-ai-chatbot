import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";


function MessageList({
  messages,
  isLoading,
  messagesEndRef,
}) {
  const safeMessages = Array.isArray(messages)
    ? messages.filter(Boolean)
    : [];

  const lastMessage =
    safeMessages.at(-1);

  const hasStreamingAssistant =
    lastMessage?.role === "assistant" &&
    lastMessage.content === "";

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
        />
      ))}

      {isLoading &&
        !hasStreamingAssistant && (
          <TypingIndicator />
        )}

      <div
        ref={messagesEndRef}
        aria-hidden="true"
      />
    </div>
  );
}


export default MessageList;