function PreviewAvatar({
  settings,
  assistant,
}) {
  if (settings.avatar_url) {
    return (
      <img
        src={settings.avatar_url}
        alt=""
        className="widget-preview__avatar-image"
      />
    );
  }

  return (
    <div
      className="widget-preview__avatar-fallback"
      style={{
        background:
          settings.secondary_color,
      }}
    >
      {assistant?.display_name
        ?.slice(0, 2)
        .toUpperCase() || "AI"}
    </div>
  );
}


export default function WidgetPreview({
  assistant,
  settings,
}) {
  if (!settings) {
    return null;
  }

  const darkTheme =
    settings.theme === "dark";

  const previewBackground =
    darkTheme
      ? "#111827"
      : settings.background_color;

  const previewText =
    darkTheme
      ? "#f8fafc"
      : settings.text_color;

  return (
    <div className="widget-preview-stage">
      <div className="widget-preview-stage__background">
        <div className="widget-preview-fake-site">
          <span />

          <span />

          <span />
        </div>

        <div className="widget-preview-fake-content">
          <div />

          <div />

          <div />
        </div>
      </div>

      <div
        className={
          settings.position ===
          "bottom-left"
            ? "widget-preview-wrapper widget-preview-wrapper--left"
            : "widget-preview-wrapper widget-preview-wrapper--right"
        }
      >
        <section
          className="widget-preview"
          style={{
            width:
              `${Math.min(
                settings.widget_width,
                440,
              )}px`,

            height:
              `${Math.min(
                settings.widget_height,
                610,
              )}px`,

            borderRadius:
              `${settings.border_radius}px`,

            background:
              previewBackground,

            color:
              previewText,

            fontFamily:
              settings.font_family,

            fontSize:
              `${settings.font_size}px`,
          }}
        >
          <header
            className="widget-preview__header"
            style={{
              background:
                `linear-gradient(
                  135deg,
                  ${settings.primary_color},
                  ${settings.secondary_color}
                )`,
            }}
          >
            <PreviewAvatar
              settings={settings}
              assistant={assistant}
            />

            <div>
              <strong>
                {assistant?.display_name ||
                  "AI Assistant"}
              </strong>

              <span>
                Online
              </span>
            </div>

            {settings.show_new_chat && (
              <button
                type="button"
                title="New chat"
              >
                +
              </button>
            )}
          </header>

          <div className="widget-preview__messages">
            <div className="widget-preview__message-row">
              <div
                className="widget-preview__message widget-preview__message--assistant"
                style={{
                  background:
                    settings.assistant_bubble_color,
                  color:
                    darkTheme
                      ? "#111827"
                      : settings.text_color,
                }}
              >
                {
                  settings.welcome_message
                }

                {settings.show_timestamps && (
                  <small>
                    10:42 AM
                  </small>
                )}
              </div>
            </div>

            <div className="widget-preview__message-row widget-preview__message-row--user">
              <div
                className="widget-preview__message widget-preview__message--user"
                style={{
                  background:
                    settings.user_bubble_color,
                }}
              >
                Can you help me?

                {settings.show_timestamps && (
                  <small>
                    10:43 AM
                  </small>
                )}
              </div>
            </div>

            <div className="widget-preview__message-row">
              <div
                className="widget-preview__message widget-preview__message--assistant"
                style={{
                  background:
                    settings.assistant_bubble_color,
                  color:
                    darkTheme
                      ? "#111827"
                      : settings.text_color,
                }}
              >
                Of course. What would
                you like to know?
              </div>
            </div>

            <div className="widget-preview__message-actions">
              {settings.show_copy && (
                <span>
                  Copy
                </span>
              )}

              {settings.show_edit && (
                <span>
                  Edit
                </span>
              )}

              {settings.show_regenerate && (
                <span>
                  Regenerate
                </span>
              )}
            </div>
          </div>

          <footer className="widget-preview__footer">
            <div
              className="widget-preview__input"
              style={{
                color:
                  darkTheme
                    ? "#94a3b8"
                    : "#94a3b8",
              }}
            >
              {settings.placeholder}

              <button
                type="button"
                style={{
                  background:
                    settings.primary_color,
                }}
              >
                ↑
              </button>
            </div>
          </footer>
        </section>

        <div
          className="widget-preview__launcher"
          style={{
            width:
              `${Math.min(
                settings.launcher_size,
                80,
              )}px`,
            height:
              `${Math.min(
                settings.launcher_size,
                80,
              )}px`,
            background:
              settings.primary_color,
          }}
        >
          {settings.launcher_icon ? (
            <img
              src={
                settings.launcher_icon
              }
              alt=""
            />
          ) : (
            <span>
              QX
            </span>
          )}
        </div>
      </div>
    </div>
  );
}