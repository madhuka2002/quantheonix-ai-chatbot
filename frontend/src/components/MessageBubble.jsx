import CopyButton from "./CopyButton";
import MarkdownMessage from "./MarkdownMessage";


function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <article
      className={`message message--${message.role}`}
    >
      <div className="message__header">
        <span className="message__sender">
          {isUser ? "You" : "Quantheonix"}
        </span>

        <CopyButton
          text={message.content}
          defaultLabel="Copy"
          copiedLabel="Copied"
          className="message__copy-button"
        />
      </div>

      {isUser ? (
        <p className="message__plain-text">
          {message.content}
        </p>
      ) : (
        <MarkdownMessage
          content={message.content}
        />
      )}
    </article>
  );
}


export default MessageBubble;