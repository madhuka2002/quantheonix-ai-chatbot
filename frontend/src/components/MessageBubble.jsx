import {
  useEffect,
  useRef,
  useState,
} from "react";

import CopyButton from "./CopyButton";
import MarkdownMessage from "./MarkdownMessage";


function MessageBubble({
  message,
  canRegenerate = false,
  canEdit = false,
  isStreaming = false,
  onRegenerate,
  onEdit,
}) {
  const [isEditing, setIsEditing] =
    useState(false);

  const [editedContent, setEditedContent] =
    useState("");

  const editTextareaRef = useRef(null);

  useEffect(() => {
    if (!isEditing) {
      return;
    }

    editTextareaRef.current?.focus();
    editTextareaRef.current?.select();
  }, [isEditing]);

  if (!message) {
    return null;
  }

  const isUser =
    message.role === "user";

  const content =
    typeof message.content === "string"
      ? message.content
      : "";

  function handleStartEditing() {
    setEditedContent(content);
    setIsEditing(true);
  }

  function handleCancelEditing() {
    setEditedContent("");
    setIsEditing(false);
  }

  async function handleSaveEditing() {
    const cleanedContent =
      editedContent.trim();

    if (
      !cleanedContent ||
      cleanedContent === content ||
      typeof onEdit !== "function"
    ) {
      handleCancelEditing();
      return;
    }

    const result = await onEdit(
      message.id,
      cleanedContent,
    );

    if (result !== false) {
      setIsEditing(false);
      setEditedContent("");
    }
  }

  function handleEditKeyDown(event) {
    if (event.key === "Escape") {
      event.preventDefault();
      handleCancelEditing();
      return;
    }

    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.nativeEvent?.isComposing
    ) {
      event.preventDefault();
      void handleSaveEditing();
    }
  }

  return (
    <article
      className={`message message--${message.role}`}
    >
      <div className="message__header">
        <span className="message__sender">
          {isUser
            ? "You"
            : "Quantheonix"}
        </span>

        <div className="message__actions">
          {!isEditing && (
            <CopyButton
              text={content}
              defaultLabel="Copy"
              copiedLabel="Copied"
              className="message__copy-button"
            />
          )}

          {canEdit &&
            !isEditing && (
              <button
                className="message__edit-button"
                type="button"
                onClick={handleStartEditing}
                disabled={isStreaming}
                title="Edit message"
              >
                Edit
              </button>
            )}

          {canRegenerate &&
            !isEditing && (
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
      </div>

      <div className="message__content">
        {isEditing ? (
          <div className="message__edit-panel">
            <textarea
              ref={editTextareaRef}
              className="message__edit-textarea"
              value={editedContent}
              onChange={(event) =>
                setEditedContent(
                  event.target.value,
                )
              }
              onKeyDown={handleEditKeyDown}
              disabled={isStreaming}
              rows={4}
              aria-label="Edit message"
            />

            <div className="message__edit-actions">
              <button
                className="message__edit-cancel"
                type="button"
                onClick={handleCancelEditing}
                disabled={isStreaming}
              >
                Cancel
              </button>

              <button
                className="message__edit-save"
                type="button"
                onClick={() =>
                  void handleSaveEditing()
                }
                disabled={
                  isStreaming ||
                  !editedContent.trim() ||
                  editedContent.trim() ===
                    content
                }
              >
                Save & send
              </button>
            </div>

            <p className="message__edit-hint">
              Enter to save · Shift + Enter for a new line · Esc to cancel
            </p>
          </div>
        ) : isUser ? (
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