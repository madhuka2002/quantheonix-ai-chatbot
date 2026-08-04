import CopyButton from "./CopyButton";
import MarkdownMessage from "./MarkdownMessage";


function MessageBubble({
  message,
  canRegenerate = false,
  isStreaming = false,
  onRegenerate,
}) {
  if (!message) {
    return null;
  }

  const isUser = message.role === "user";

  const content =
    typeof message.content === "string"
      ? message.content
      : "";

  return (
    <article
      className={`message message--${message.role}`}
    >
      <div className="message__header">
        <span className="message__sender">
          {isUser ? "You" : "Quantheonix"}
        </span>

        <CopyButton
          text={content}
          defaultLabel="Copy"
          copiedLabel="Copied"
          className="message__copy-button"
        />

        {canRegenerate && (
          <button
            className="message__regenerate-button"
            type="button"
            onClick={onRegenerate}
            disabled={isStreaming}
            title="Regenerate response"
          >
            Regenerate
          </button>
        )}
      </div>

      <div className="message__content">
        {isUser ? (
          <p className="message__plain-text">
            {content}
          </p>
        ) : (
          <MarkdownMessage
            content={content}
          />
        )}
      </div>
    </article>
  );
}


export default MessageBubble;