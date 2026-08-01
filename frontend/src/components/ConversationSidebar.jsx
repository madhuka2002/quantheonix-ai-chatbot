function formatConversationDate(
  dateValue,
) {
  if (!dateValue) {
    return "";
  }

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      month: "short",
      day: "numeric",
    },
  ).format(date);
}


export default function ConversationSidebar({
  conversations,
  activeConversationId,
  isLoading,
  error,
  user,
  onSelectConversation,
  onDeleteConversation,
  onNewChat,
  onRefresh,
  onLogout,
}) {
  return (
    <aside className="conversation-sidebar">
      <div className="sidebar-top">
        <div className="sidebar-brand">
          <div className="sidebar-logo">
            QX
          </div>

          <div>
            <strong>Quantheonix AI</strong>
            <span>Assistant</span>
          </div>
        </div>

        <button
          className="sidebar-new-chat"
          type="button"
          onClick={onNewChat}
        >
          + New chat
        </button>
      </div>

      <div className="sidebar-history-header">
        <span>Conversations</span>

        <button
          type="button"
          onClick={onRefresh}
          disabled={isLoading}
          aria-label="Refresh conversations"
          title="Refresh conversations"
        >
          ↻
        </button>
      </div>

      <div className="sidebar-conversations">
        {isLoading && (
          <p className="sidebar-status">
            Loading conversations...
          </p>
        )}

        {!isLoading && error && (
          <p className="sidebar-error">
            {error}
          </p>
        )}

        {!isLoading &&
          !error &&
          conversations.length === 0 && (
            <p className="sidebar-status">
              No conversations yet.
            </p>
          )}

        {conversations.map(
          (conversation) => {
            const isActive =
              conversation.id ===
              activeConversationId;

            return (
              <div
                className={
                  isActive
                    ? "sidebar-conversation active"
                    : "sidebar-conversation"
                }
                key={conversation.id}
              >
                <button
                  className="conversation-open"
                  type="button"
                  onClick={() =>
                    onSelectConversation(
                      conversation.id,
                    )
                  }
                >
                  <span className="conversation-title">
                    {conversation.title ||
                      "Untitled conversation"}
                  </span>

                  <span className="conversation-meta">
                    {conversation.message_count ?? 0}
                    {" messages · "}
                    {formatConversationDate(
                      conversation.updated_at,
                    )}
                  </span>
                </button>

                <button
                  className="conversation-delete"
                  type="button"
                  onClick={() =>
                    onDeleteConversation(
                      conversation.id,
                    )
                  }
                  aria-label="Delete conversation"
                  title="Delete conversation"
                >
                  ×
                </button>
              </div>
            );
          },
        )}
      </div>

      <div className="sidebar-user">
        <div>
          <strong>
            {user?.full_name ||
              user?.username ||
              "User"}
          </strong>

          <span>
            {user?.email || ""}
          </span>
        </div>

        <button
          type="button"
          onClick={onLogout}
        >
          Log out
        </button>
      </div>
    </aside>
  );
}