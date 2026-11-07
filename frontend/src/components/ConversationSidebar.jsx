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
  search,
  onSearchChange,
  onSelectConversation,
  onDeleteConversation,
  onRenameConversation,
  onNewChat,
  onRefresh,
  isOpen = false,
  onClose,
}) {
  const cleanedSearch = (
    search || ""
  )
    .trim()
    .toLowerCase();

  const visibleConversations =
    cleanedSearch
      ? conversations.filter(
          (conversation) => {
            const title = (
              conversation.title ||
              "Untitled conversation"
            ).toLowerCase();

            return title.includes(
              cleanedSearch,
            );
          },
        )
      : conversations;


  return (
    <aside
      className={
        isOpen
          ? "conversation-sidebar conversation-sidebar--open"
          : "conversation-sidebar"
      }
      aria-label="Conversation history"
    >
      <div className="sidebar-top">
        <div className="sidebar-brand">
          <div className="sidebar-logo">
            QX
          </div>

          <div>
            <strong>Chat history</strong>
            <span>Test conversations</span>
          </div>

          <button
            className="sidebar-close"
            type="button"
            onClick={onClose}
            aria-label="Close history"
          >
            ×
          </button>
        </div>

        <button
          className="sidebar-new-chat"
          type="button"
          onClick={onNewChat}
        >
          + New chat
        </button>

        <input
          className="sidebar-search"
          type="search"
          value={search}
          onChange={(event) =>
            onSearchChange(
              event.target.value,
            )
          }
          placeholder="Search conversations"
          aria-label="Search conversations"
        />
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
          visibleConversations.length === 0 && (
            <p className="sidebar-status">
              {cleanedSearch
                ? "No matching conversations."
                : "No conversations yet."}
            </p>
          )}

        {!isLoading &&
          !error &&
          visibleConversations.map(
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
                      {conversation.message_count ??
                        0}
                      {" messages · "}
                      {formatConversationDate(
                        conversation.updated_at,
                      )}
                    </span>
                  </button>

                  <button
                    className="conversation-rename"
                    type="button"
                    onClick={() => {
                      const nextTitle =
                        window.prompt(
                          "Enter a new conversation title:",
                          conversation.title ||
                            "",
                        );

                      const cleanedTitle =
                        nextTitle?.trim();

                      if (cleanedTitle) {
                        onRenameConversation(
                          conversation.id,
                          cleanedTitle,
                        );
                      }
                    }}
                    aria-label="Rename conversation"
                    title="Rename conversation"
                  >
                    ✎
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

    </aside>
  );
}
