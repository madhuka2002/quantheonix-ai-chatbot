import {
  useState,
} from "react";

import {
  updateAssistant,
} from "../../services/assistantApi";

import FieldHelp
  from "../components/FieldHelp";


function createInitialForm(
  assistant,
) {
  return {
    system_prompt:
      assistant?.system_prompt ?? "",

    tone:
      assistant?.tone ??
      "professional",

    temperature:
      assistant?.temperature ?? 0.5,

    model_name:
      assistant?.model_name ??
      "gemini-flash-latest",

    rag_enabled:
      assistant?.rag_enabled ?? false,

    is_active:
      assistant?.is_active ?? true,
  };
}


export default function AISettingsPage({
  assistant,
  onAssistantUpdated,
}) {
  const [
    form,
    setForm,
  ] = useState(
    () =>
      createInitialForm(
        assistant,
      ),
  );

  const [
    savedForm,
    setSavedForm,
  ] = useState(
    () =>
      createInitialForm(
        assistant,
      ),
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


  if (!assistant) {
    return (
      <div className="dashboard-page">
        <section className="dashboard-empty-state">
          <strong>
            Select an assistant
          </strong>

          <p>
            Choose an assistant before
            configuring its AI
            behavior.
          </p>
        </section>
      </div>
    );
  }


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

    if (
      type === "checkbox"
    ) {
      nextValue = checked;
    } else if (
      type === "range"
    ) {
      nextValue =
        Number(value);
    } else {
      nextValue = value;
    }

    setForm(
      (current) => ({
        ...current,
        [name]: nextValue,
      }),
    );

    setSuccessMessage("");
  }


  function handleReset() {
    setForm({
      ...savedForm,
    });

    setError("");
    setSuccessMessage("");
  }


  async function handleSave(
    event,
  ) {
    event.preventDefault();

    setIsSaving(true);
    setError("");
    setSuccessMessage("");

    const payload = {
      system_prompt:
        form.system_prompt.trim() ||
        null,

      tone:
        form.tone,

      temperature:
        Number(
          form.temperature,
        ),

      model_name:
        form.model_name.trim(),

      rag_enabled:
        form.rag_enabled,

      is_active:
        form.is_active,
    };

    try {
      const updatedAssistant =
        await updateAssistant(
          assistant.id,
          payload,
        );

      const nextForm =
        createInitialForm(
          updatedAssistant,
        );

      setForm(
        nextForm,
      );

      setSavedForm(
        nextForm,
      );

      setSuccessMessage(
        "AI settings saved successfully.",
      );

      if (
        onAssistantUpdated
      ) {
        await onAssistantUpdated();
      }
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "AI settings could not be saved.",
      );
    } finally {
      setIsSaving(false);
    }
  }


  const hasChanges =
    JSON.stringify(form) !==
    JSON.stringify(savedForm);


  return (
    <div className="dashboard-page">
      <section className="ai-settings-header">
        <div>
          <span className="dashboard-eyebrow">
            AI Configuration
          </span>

          <h2>
            {
              assistant.display_name
            } intelligence
          </h2>

          <p>
            Configure how this
            assistant behaves,
            responds and uses AI.
          </p>
        </div>

        <div className="ai-settings-header__actions">
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
            type="submit"
            form="ai-settings-form"
            className="dashboard-primary-button"
            disabled={
              !hasChanges ||
              isSaving
            }
          >
            {isSaving
              ? "Saving..."
              : "Save settings"}
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


      <form
        id="ai-settings-form"
        className="ai-settings-layout"
        onSubmit={
          handleSave
        }
      >
        <div className="ai-settings-main">
          <section className="ai-settings-card">
            <div className="ai-settings-card__heading">
              <span>
                01
              </span>

              <div>
                <h3>
                  Instructions
                </h3>

                <p>
                  Define the assistant's
                  role and behavior.
                </p>
              </div>
            </div>


            <label className="widget-field">
              <span className="widget-field__label">
                System prompt

                <FieldHelp
                  text="The main instruction sent to the AI. Use it to define the assistant's role, behavior, restrictions and response style."
                />
              </span>

              <textarea
                name="system_prompt"
                rows={10}
                value={
                  form.system_prompt
                }
                onChange={
                  handleFieldChange
                }
                placeholder={
                  "You are a helpful customer support assistant..."
                }
              />
            </label>

            <div className="ai-prompt-help">
              <strong>
                Prompt tips
              </strong>

              <p>
                Include the assistant's
                purpose, what it should
                help with, how it
                should respond, and
                anything it should
                avoid.
              </p>
            </div>
          </section>


          <section className="ai-settings-card">
            <div className="ai-settings-card__heading">
              <span>
                02
              </span>

              <div>
                <h3>
                  Response behavior
                </h3>

                <p>
                  Control style and
                  response variation.
                </p>
              </div>
            </div>


            <div className="widget-field-grid">
              <label className="widget-field">
                <span className="widget-field__label">
                  Tone

                  <FieldHelp
                    text="Controls the general communication style of the assistant."
                  />
                </span>

                <select
                  name="tone"
                  value={
                    form.tone
                  }
                  onChange={
                    handleFieldChange
                  }
                >
                  <option value="professional">
                    Professional
                  </option>

                  <option value="friendly">
                    Friendly
                  </option>

                  <option value="concise">
                    Concise
                  </option>

                  <option value="technical">
                    Technical
                  </option>
                </select>
              </label>


              <label className="widget-field">
                <span className="widget-field__label">
                  Temperature

                  <FieldHelp
                    text="Controls response variation. Lower values are more predictable; higher values allow more varied responses."
                  />
                </span>

                <div className="widget-range-field">
                  <input
                    type="range"
                    name="temperature"
                    min="0"
                    max="2"
                    step="0.1"
                    value={
                      form.temperature
                    }
                    onChange={
                      handleFieldChange
                    }
                  />

                  <strong>
                    {
                      form.temperature
                    }
                  </strong>
                </div>
              </label>
            </div>


            <div className="temperature-scale">
              <span>
                Precise
              </span>

              <span>
                Balanced
              </span>

              <span>
                Creative
              </span>
            </div>
          </section>


          <section className="ai-settings-card">
            <div className="ai-settings-card__heading">
              <span>
                03
              </span>

              <div>
                <h3>
                  AI model
                </h3>

                <p>
                  Choose which model
                  powers this
                  assistant.
                </p>
              </div>
            </div>


            <label className="widget-field">
              <span className="widget-field__label">
                Model name

                <FieldHelp
                  text="The backend model identifier used for this assistant. The configured AI provider must support this model."
                />
              </span>

              <input
                type="text"
                name="model_name"
                value={
                  form.model_name
                }
                onChange={
                  handleFieldChange
                }
                placeholder="gemini-flash-latest"
                required
              />
            </label>


            <div className="ai-model-info">
              <div className="ai-model-info__icon">
                AI
              </div>

              <div>
                <strong>
                  {
                    form.model_name ||
                    "No model selected"
                  }
                </strong>

                <span>
                  Current assistant
                  model
                </span>
              </div>
            </div>
          </section>
        </div>


        <aside className="ai-settings-side">
          <section className="ai-settings-card">
            <div className="ai-settings-card__heading">
              <span>
                04
              </span>

              <div>
                <h3>
                  Capabilities
                </h3>

                <p>
                  Enable optional AI
                  features.
                </p>
              </div>
            </div>


            <label className="ai-feature-toggle">
              <div>
                <strong>
                  RAG knowledge
                </strong>

                <span>
                  Allow this assistant
                  to use its connected
                  knowledge base.
                </span>
              </div>

              <input
                type="checkbox"
                name="rag_enabled"
                checked={
                  form.rag_enabled
                }
                onChange={
                  handleFieldChange
                }
              />
            </label>


            {form.rag_enabled && (
              <div className="ai-feature-notice">
                <strong>
                  RAG enabled
                </strong>

                <p>
                  The assistant is
                  configured to use
                  retrieval-augmented
                  generation when the
                  knowledge system is
                  connected.
                </p>
              </div>
            )}
          </section>


          <section className="ai-settings-card">
            <div className="ai-settings-card__heading">
              <span>
                05
              </span>

              <div>
                <h3>
                  Availability
                </h3>

                <p>
                  Control whether this
                  assistant can be
                  used.
                </p>
              </div>
            </div>


            <label className="ai-feature-toggle">
              <div>
                <strong>
                  Assistant active
                </strong>

                <span>
                  Disable this to stop
                  the assistant from
                  being available.
                </span>
              </div>

              <input
                type="checkbox"
                name="is_active"
                checked={
                  form.is_active
                }
                onChange={
                  handleFieldChange
                }
              />
            </label>


            <div
              className={
                form.is_active
                  ? "assistant-state assistant-state--active"
                  : "assistant-state"
              }
            >
              <span />

              {form.is_active
                ? "Assistant is active"
                : "Assistant is inactive"}
            </div>
          </section>


          <section className="ai-settings-summary">
            <span className="dashboard-eyebrow">
              Current Configuration
            </span>

            <div>
              <span>
                Tone
              </span>

              <strong>
                {form.tone}
              </strong>
            </div>

            <div>
              <span>
                Temperature
              </span>

              <strong>
                {
                  form.temperature
                }
              </strong>
            </div>

            <div>
              <span>
                Model
              </span>

              <strong>
                {
                  form.model_name
                }
              </strong>
            </div>

            <div>
              <span>
                RAG
              </span>

              <strong>
                {form.rag_enabled
                  ? "Enabled"
                  : "Disabled"}
              </strong>
            </div>
          </section>
        </aside>
      </form>
    </div>
  );
}