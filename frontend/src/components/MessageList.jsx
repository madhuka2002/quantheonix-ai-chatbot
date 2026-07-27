import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";


function MessageList({
  messages,
  isLoading,
  messagesEndRef,
}) {
  return (
    <div
      className="chat__messages"
      aria-live="polite"
      aria-label="Chat messages"
    >
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
        />
      ))}

      {isLoading && <TypingIndicator />}

      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList;