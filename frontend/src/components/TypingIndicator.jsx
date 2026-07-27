function TypingIndicator() {
  return (
    <article
      className="message message--assistant"
      aria-label="Quantheonix is typing"
    >
      <span className="message__sender">
        Quantheonix
      </span>

      <div className="typing-indicator">
        <span />
        <span />
        <span />
      </div>
    </article>
  );
}

export default TypingIndicator;