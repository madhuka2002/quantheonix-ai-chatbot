function ErrorBanner({
  error,
  failedMessage,
  isLoading,
  onRetry,
}) {
  if (!error) {
    return null;
  }

  return (
    <div
      className="chat__error"
      role="alert"
    >
      <p>{error}</p>

      {failedMessage && (
        <button
          type="button"
          onClick={onRetry}
          disabled={isLoading}
        >
          Retry
        </button>
      )}
    </div>
  );
}

export default ErrorBanner;