import {
  useEffect,
  useState,
} from "react";

import {
  getWidgetSettings,
  updateWidgetSettings,
} from "../../services/widgetApi";

import FieldHelp
  from "../components/FieldHelp";

import WidgetPreview
  from "../components/WidgetPreview";


function ColorField({
  label,
  help,
  name,
  value,
  onChange,
}) {
  return (
    <label className="widget-field">
      <span className="widget-field__label">
        {label}

        <FieldHelp
          text={help}
        />
      </span>

      <div className="widget-color-field">
        <input
          type="color"
          name={name}
          value={value}
          onChange={onChange}
        />

        <input
          type="text"
          name={name}
          value={value}
          onChange={onChange}
          pattern="^#[0-9A-Fa-f]{6}$"
          maxLength={7}
        />
      </div>
    </label>
  );
}


function ToggleField({
  label,
  help,
  name,
  checked,
  onChange,
}) {
  return (
    <label className="widget-toggle">
      <div>
        <span>
          {label}

          <FieldHelp
            text={help}
          />
        </span>
      </div>

      <input
        type="checkbox"
        name={name}
        checked={checked}
        onChange={onChange}
      />
    </label>
  );
}


export default function CustomizePage({
  assistant,
}) {
  const [
    settings,
    setSettings,
  ] = useState(null);

  const [
    savedSettings,
    setSavedSettings,
  ] = useState(null);

  const [
    isLoading,
    setIsLoading,
  ] = useState(
    () => Boolean(assistant?.id),
  );

  const [
    isSaving,
    setIsSaving,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  const [
    successMessage,
    setSuccessMessage,
  ] = useState("");


  useEffect(() => {
    if (!assistant?.id) {
      return undefined;
    }

    let cancelled = false;

    async function loadSettings() {
      try {
        const data =
          await getWidgetSettings(
            assistant.id,
          );

        if (cancelled) {
          return;
        }

        setSettings(data);
        setSavedSettings(data);
        setError("");
        setSuccessMessage("");
        setIsLoading(false);
      } catch (requestError) {
        if (cancelled) {
          return;
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Widget settings could not be loaded.",
        );

        setIsLoading(false);
      }
    }

    void loadSettings();

    return () => {
      cancelled = true;
    };
  }, [assistant?.id]);


  function handleFieldChange(
    event,
  ) {
    const {
      name,
      value,
      type,
      checked,
    } = event.target;

    let nextValue;

    if (type === "checkbox") {
      nextValue = checked;
    } else if (
      type === "range" ||
      type === "number"
    ) {
      nextValue = Number(value);
    } else {
      nextValue = value;
    }

    setSettings(
      (current) => ({
        ...current,
        [name]: nextValue,
      }),
    );

    setSuccessMessage("");
  }


  function handleReset() {
    if (!savedSettings) {
      return;
    }

    setSettings({
      ...savedSettings,
    });

    setSuccessMessage("");
    setError("");
  }


  async function handleSave() {
    if (
      !assistant?.id ||
      !settings
    ) {
      return;
    }

    setIsSaving(true);
    setError("");
    setSuccessMessage("");

    const payload = {
      welcome_message:
        settings.welcome_message,

      placeholder:
        settings.placeholder,

      position:
        settings.position,

      primary_color:
        settings.primary_color,

      secondary_color:
        settings.secondary_color,

      background_color:
        settings.background_color,

      text_color:
        settings.text_color,

      assistant_bubble_color:
        settings.assistant_bubble_color,

      user_bubble_color:
        settings.user_bubble_color,

      font_family:
        settings.font_family,

      font_size:
        settings.font_size,

      avatar_url:
        settings.avatar_url || null,

      widget_width:
        settings.widget_width,

      widget_height:
        settings.widget_height,

      border_radius:
        settings.border_radius,

      launcher_size:
        settings.launcher_size,

      launcher_icon:
        settings.launcher_icon || null,

      theme:
        settings.theme,

      show_copy:
        settings.show_copy,

      show_edit:
        settings.show_edit,

      show_regenerate:
        settings.show_regenerate,

      show_new_chat:
        settings.show_new_chat,

      show_timestamps:
        settings.show_timestamps,

      initially_open:
        settings.initially_open,
    };

    try {
      const updated =
        await updateWidgetSettings(
          assistant.id,
          payload,
        );

      setSettings(updated);
      setSavedSettings(updated);

      setSuccessMessage(
        "Widget settings saved successfully.",
      );
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Widget settings could not be saved.",
      );
    } finally {
      setIsSaving(false);
    }
  }


  if (!assistant) {
    return (
      <div className="dashboard-page">
        <section className="dashboard-empty-state">
          <strong>
            Select an assistant
          </strong>

          <p>
            Choose an assistant from
            the Assistants page before
            customizing its widget.
          </p>
        </section>
      </div>
    );
  }


  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div className="widget-studio-loading">
          Loading widget settings...
        </div>
      </div>
    );
  }


  if (!settings) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-error">
          {error ||
            "Widget settings are unavailable."}
        </div>
      </div>
    );
  }


  const hasChanges =
    JSON.stringify(settings) !==
    JSON.stringify(savedSettings);


  return (
    <div className="dashboard-page">
      <section className="widget-studio-header">
        <div>
          <span className="dashboard-eyebrow">
            Widget Studio
          </span>

          <h2>
            Customize {
              assistant.display_name
            }
          </h2>

          <p>
            Changes appear instantly
            in the preview. Save when
            you are happy with the
            result.
          </p>
        </div>

        <div className="widget-studio-header__actions">
          <button
            type="button"
            className="dashboard-secondary-button"
            disabled={
              !hasChanges ||
              isSaving
            }
            onClick={
              handleReset
            }
          >
            Reset
          </button>

          <button
            type="button"
            className="dashboard-primary-button"
            disabled={
              !hasChanges ||
              isSaving
            }
            onClick={
              handleSave
            }
          >
            {isSaving
              ? "Saving..."
              : "Save changes"}
          </button>
        </div>
      </section>


      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="dashboard-success">
          {successMessage}
        </div>
      )}


      <div className="widget-studio">
        <div className="widget-studio__controls">
          <section className="widget-control-section">
            <div className="widget-control-section__heading">
              <span>
                01
              </span>

              <div>
                <h3>
                  Content
                </h3>

                <p>
                  Configure the text
                  users see when they
                  open the chatbot.
                </p>
              </div>
            </div>


            <label className="widget-field">
              <span className="widget-field__label">
                Welcome message

                <FieldHelp
                  text="The first message shown when a user opens the chatbot."
                />
              </span>

              <textarea
                name="welcome_message"
                rows={3}
                maxLength={500}
                value={
                  settings.welcome_message
                }
                onChange={
                  handleFieldChange
                }
              />
            </label>


            <label className="widget-field">
              <span className="widget-field__label">
                Input placeholder

                <FieldHelp
                  text="The text shown inside the message box before the user starts typing."
                />
              </span>

              <input
                type="text"
                name="placeholder"
                maxLength={150}
                value={
                  settings.placeholder
                }
                onChange={
                  handleFieldChange
                }
              />
            </label>
          </section>


          <section className="widget-control-section">
            <div className="widget-control-section__heading">
              <span>
                02
              </span>

              <div>
                <h3>
                  Appearance
                </h3>

                <p>
                  Match the chatbot to
                  your website or
                  product branding.
                </p>
              </div>
            </div>


            <div className="widget-color-grid">
              <ColorField
                label="Primary"
                help="Main brand color used for the chatbot header, launcher and important actions."
                name="primary_color"
                value={
                  settings.primary_color
                }
                onChange={
                  handleFieldChange
                }
              />

              <ColorField
                label="Secondary"
                help="Supporting accent color used with the primary brand color."
                name="secondary_color"
                value={
                  settings.secondary_color
                }
                onChange={
                  handleFieldChange
                }
              />

              <ColorField
                label="Background"
                help="Main background color inside the chatbot window."
                name="background_color"
                value={
                  settings.background_color
                }
                onChange={
                  handleFieldChange
                }
              />

              <ColorField
                label="Text"
                help="Main text color used throughout the chatbot."
                name="text_color"
                value={
                  settings.text_color
                }
                onChange={
                  handleFieldChange
                }
              />

              <ColorField
                label="Assistant bubble"
                help="Background color for messages sent by the AI assistant."
                name="assistant_bubble_color"
                value={
                  settings.assistant_bubble_color
                }
                onChange={
                  handleFieldChange
                }
              />

              <ColorField
                label="User bubble"
                help="Background color for messages sent by the visitor."
                name="user_bubble_color"
                value={
                  settings.user_bubble_color
                }
                onChange={
                  handleFieldChange
                }
              />
            </div>


            <div className="widget-field-grid">
              <label className="widget-field">
                <span className="widget-field__label">
                  Theme

                  <FieldHelp
                    text="Switch the overall chatbot appearance between light and dark mode."
                  />
                </span>

                <select
                  name="theme"
                  value={
                    settings.theme
                  }
                  onChange={
                    handleFieldChange
                  }
                >
                  <option value="light">
                    Light
                  </option>

                  <option value="dark">
                    Dark
                  </option>
                </select>
              </label>


              <label className="widget-field">
                <span className="widget-field__label">
                  Position

                  <FieldHelp
                    text="Choose which bottom corner of the website contains the chatbot launcher."
                  />
                </span>

                <select
                  name="position"
                  value={
                    settings.position
                  }
                  onChange={
                    handleFieldChange
                  }
                >
                  <option value="bottom-right">
                    Bottom right
                  </option>

                  <option value="bottom-left">
                    Bottom left
                  </option>
                </select>
              </label>
            </div>
          </section>


          <section className="widget-control-section">
            <div className="widget-control-section__heading">
              <span>
                03
              </span>

              <div>
                <h3>
                  Typography
                </h3>

                <p>
                  Control the chatbot
                  font and reading
                  size.
                </p>
              </div>
            </div>


            <div className="widget-field-grid">
              <label className="widget-field">
                <span className="widget-field__label">
                  Font family

                  <FieldHelp
                    text="CSS font-family name used by the widget. The website must have the font available for custom fonts."
                  />
                </span>

                <select
                  name="font_family"
                  value={
                    settings.font_family
                  }
                  onChange={
                    handleFieldChange
                  }
                >
                  <option value="Inter">
                    Inter
                  </option>

                  <option value="Arial">
                    Arial
                  </option>

                  <option value="Roboto">
                    Roboto
                  </option>

                  <option value="Poppins">
                    Poppins
                  </option>

                  <option value="system-ui">
                    System UI
                  </option>
                </select>
              </label>


              <label className="widget-field">
                <span className="widget-field__label">
                  Font size

                  <FieldHelp
                    text="Base font size inside the chatbot. Allowed range is 10 to 24 pixels."
                  />
                </span>

                <div className="widget-range-field">
                  <input
                    type="range"
                    name="font_size"
                    min="10"
                    max="24"
                    value={
                      settings.font_size
                    }
                    onChange={
                      handleFieldChange
                    }
                  />

                  <strong>
                    {
                      settings.font_size
                    }px
                  </strong>
                </div>
              </label>
            </div>
          </section>


          <section className="widget-control-section">
            <div className="widget-control-section__heading">
              <span>
                04
              </span>

              <div>
                <h3>
                  Size & layout
                </h3>

                <p>
                  Control the chatbot
                  window dimensions.
                </p>
              </div>
            </div>


            <div className="widget-field-grid">
              <label className="widget-field">
                <span className="widget-field__label">
                  Width

                  <FieldHelp
                    text="Width of the chatbot window. Allowed range is 280 to 800 pixels."
                  />
                </span>

                <div className="widget-range-field">
                  <input
                    type="range"
                    name="widget_width"
                    min="280"
                    max="800"
                    step="10"
                    value={
                      settings.widget_width
                    }
                    onChange={
                      handleFieldChange
                    }
                  />

                  <strong>
                    {
                      settings.widget_width
                    }px
                  </strong>
                </div>
              </label>


              <label className="widget-field">
                <span className="widget-field__label">
                  Height

                  <FieldHelp
                    text="Height of the chatbot window. Allowed range is 350 to 1000 pixels."
                  />
                </span>

                <div className="widget-range-field">
                  <input
                    type="range"
                    name="widget_height"
                    min="350"
                    max="1000"
                    step="10"
                    value={
                      settings.widget_height
                    }
                    onChange={
                      handleFieldChange
                    }
                  />

                  <strong>
                    {
                      settings.widget_height
                    }px
                  </strong>
                </div>
              </label>


              <label className="widget-field">
                <span className="widget-field__label">
                  Border radius

                  <FieldHelp
                    text="Controls how rounded the chatbot window corners are."
                  />
                </span>

                <div className="widget-range-field">
                  <input
                    type="range"
                    name="border_radius"
                    min="0"
                    max="50"
                    value={
                      settings.border_radius
                    }
                    onChange={
                      handleFieldChange
                    }
                  />

                  <strong>
                    {
                      settings.border_radius
                    }px
                  </strong>
                </div>
              </label>


              <label className="widget-field">
                <span className="widget-field__label">
                  Launcher size

                  <FieldHelp
                    text="Size of the circular button users click to open the chatbot."
                  />
                </span>

                <div className="widget-range-field">
                  <input
                    type="range"
                    name="launcher_size"
                    min="40"
                    max="100"
                    value={
                      settings.launcher_size
                    }
                    onChange={
                      handleFieldChange
                    }
                  />

                  <strong>
                    {
                      settings.launcher_size
                    }px
                  </strong>
                </div>
              </label>
            </div>
          </section>


          <section className="widget-control-section">
            <div className="widget-control-section__heading">
              <span>
                05
              </span>

              <div>
                <h3>
                  Branding
                </h3>

                <p>
                  Add optional images
                  for the assistant and
                  launcher.
                </p>
              </div>
            </div>


            <label className="widget-field">
              <span className="widget-field__label">
                Assistant avatar URL

                <FieldHelp
                  text="Optional public URL for the avatar displayed beside the assistant name."
                />
              </span>

              <input
                type="url"
                name="avatar_url"
                value={
                  settings.avatar_url ||
                  ""
                }
                onChange={
                  handleFieldChange
                }
                placeholder="https://example.com/avatar.png"
              />
            </label>


            <label className="widget-field">
              <span className="widget-field__label">
                Launcher icon URL

                <FieldHelp
                  text="Optional public image URL used inside the floating chatbot launcher button."
                />
              </span>

              <input
                type="url"
                name="launcher_icon"
                value={
                  settings.launcher_icon ||
                  ""
                }
                onChange={
                  handleFieldChange
                }
                placeholder="https://example.com/chat-icon.svg"
              />
            </label>
          </section>


          <section className="widget-control-section">
            <div className="widget-control-section__heading">
              <span>
                06
              </span>

              <div>
                <h3>
                  Features
                </h3>

                <p>
                  Decide which chatbot
                  controls visitors can
                  use.
                </p>
              </div>
            </div>


            <div className="widget-toggle-list">
              <ToggleField
                label="Copy response"
                help="Allows users to copy an assistant response."
                name="show_copy"
                checked={
                  settings.show_copy
                }
                onChange={
                  handleFieldChange
                }
              />

              <ToggleField
                label="Edit message"
                help="Allows users to edit an earlier message."
                name="show_edit"
                checked={
                  settings.show_edit
                }
                onChange={
                  handleFieldChange
                }
              />

              <ToggleField
                label="Regenerate response"
                help="Allows users to request another answer for the same message."
                name="show_regenerate"
                checked={
                  settings.show_regenerate
                }
                onChange={
                  handleFieldChange
                }
              />

              <ToggleField
                label="New chat"
                help="Displays a control that allows visitors to start a fresh conversation."
                name="show_new_chat"
                checked={
                  settings.show_new_chat
                }
                onChange={
                  handleFieldChange
                }
              />

              <ToggleField
                label="Show timestamps"
                help="Displays the time beside chatbot messages."
                name="show_timestamps"
                checked={
                  settings.show_timestamps
                }
                onChange={
                  handleFieldChange
                }
              />

              <ToggleField
                label="Initially open"
                help="Automatically opens the chatbot when the website loads instead of showing only the launcher."
                name="initially_open"
                checked={
                  settings.initially_open
                }
                onChange={
                  handleFieldChange
                }
              />
            </div>
          </section>
        </div>


        <aside className="widget-studio__preview">
          <div className="widget-preview-sticky">
            <div className="widget-preview-heading">
              <div>
                <span className="dashboard-eyebrow">
                  Live Preview
                </span>

                <h3>
                  Website preview
                </h3>
              </div>

              {hasChanges && (
                <span className="widget-unsaved-badge">
                  Unsaved
                </span>
              )}
            </div>

            <WidgetPreview
              assistant={assistant}
              settings={settings}
            />
          </div>
        </aside>
      </div>
    </div>
  );
}