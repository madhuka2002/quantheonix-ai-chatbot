function ChatInput({
  input,
  isLoading,
  isStreaming,
  isResetting,
  textareaRef,
  onInputChange,
  onKeyDown,
  onSubmit,
  onStop,
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
          maxLength={10000}
          rows={1}
          disabled={isDisabled}
          autoComplete="off"
        />

        {isStreaming ? (
          <button
            className="chat__stop-button"
            type="button"
            onClick={onStop}
          >
            Stop generating
          </button>
        ) : (
          <button
            className="chat__send-button"
            type="submit"
            disabled={
              isLoading ||
              !input.trim()
            }
          >
            Send
          </button>
        )}
      </form>

      <p className="chat__hint">
        Press Enter to send. Use Shift + Enter for a
        new line.
      </p>
    </>
  );
}

export default ChatInput;