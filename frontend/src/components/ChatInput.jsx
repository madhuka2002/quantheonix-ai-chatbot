function ChatInput({
  input,
  isLoading,
  isResetting,
  textareaRef,
  onInputChange,
  onKeyDown,
  onSubmit,
}) {
  const isDisabled = isLoading || isResetting;

  return (
    <>
      <form
        className="chat__form"
        onSubmit={onSubmit}
      >
        <label
          className="sr-only"
          htmlFor="chat-message"
        >
          Enter your message
        </label>

        <textarea
          ref={textareaRef}
          id="chat-message"
          value={input}
          onChange={onInputChange}
          onKeyDown={onKeyDown}
          placeholder="Type your message..."
          maxLength={2000}
          rows={1}
          disabled={isDisabled}
          autoComplete="off"
        />

        <button
          type="submit"
          disabled={!input.trim() || isDisabled}
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>

      <p className="chat__hint">
        Press Enter to send. Use Shift + Enter for a
        new line.
      </p>
    </>
  );
}

export default ChatInput;