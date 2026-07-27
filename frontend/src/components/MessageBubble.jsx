function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <article
      className={`message message--${message.role}`}
    >
      <span className="message__sender">
        {isUser ? "You" : "Quantheonix"}
      </span>

      <p>{message.content}</p>
    </article>
  );
}

export default MessageBubble;