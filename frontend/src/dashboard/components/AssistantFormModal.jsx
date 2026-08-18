import {
  useState,
} from "react";


const INITIAL_FORM = {
  name: "",
  display_name: "",
  description: "",
  system_prompt: "",
  tone: "professional",
  temperature: 0.5,
  model_name: "gemini-flash-latest",
  rag_enabled: false,
  is_active: true,
};


function createInitialForm(
  assistant,
) {
  if (!assistant) {
    return {
      ...INITIAL_FORM,
    };
  }

  return {
    name:
      assistant.name ?? "",

    display_name:
      assistant.display_name ?? "",

    description:
      assistant.description ?? "",

    system_prompt:
      assistant.system_prompt ?? "",

    tone:
      assistant.tone ??
      "professional",

    temperature:
      assistant.temperature ?? 0.5,

    model_name:
      assistant.model_name ??
      "gemini-flash-latest",

    rag_enabled:
      assistant.rag_enabled ?? false,

    is_active:
      assistant.is_active ?? true,
  };
}


export default function AssistantFormModal({
  assistant = null,
  isSaving = false,
  error = "",
  onClose,
  onSubmit,
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


  function updateField(
    event,
  ) {
    const {
      name,
      value,
      type,
      checked,
    } = event.target;

    setForm(
      (current) => ({
        ...current,

        [name]:
          type === "checkbox"
            ? checked
            : value,
      }),
    );
  }


  async function handleSubmit(
    event,
  ) {
    event.preventDefault();

    await onSubmit({
      ...form,

      name:
        form.name.trim(),

      display_name:
        form.display_name.trim(),

      description:
        form.description.trim() ||
        null,

      system_prompt:
        form.system_prompt.trim() ||
        null,

      temperature:
        Number(
          form.temperature,
        ),
    });
  }


  return (
    <div
      className="dashboard-modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (
          event.target ===
          event.currentTarget
        ) {
          onClose();
        }
      }}
    >
      <section
        className="dashboard-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assistant-form-title"
      >
        <header className="dashboard-modal__header">
          <div>
            <span className="dashboard-eyebrow">
              Assistant configuration
            </span>

            <h2 id="assistant-form-title">
              {assistant
                ? "Edit assistant"
                : "Create assistant"}
            </h2>
          </div>

          <button
            type="button"
            className="dashboard-modal__close"
            onClick={onClose}
            disabled={isSaving}
            aria-label="Close"
          >
            ×
          </button>
        </header>


        <form
          className="assistant-form"
          onSubmit={
            handleSubmit
          }
        >
          <div className="assistant-form__grid">
            <label>
              <span>
                Internal name
              </span>

              <input
                name="name"
                value={
                  form.name
                }
                onChange={
                  updateField
                }
                placeholder="support-bot"
                required
                minLength={2}
                maxLength={100}
              />
            </label>


            <label>
              <span>
                Display name
              </span>

              <input
                name="display_name"
                value={
                  form.display_name
                }
                onChange={
                  updateField
                }
                placeholder="Support Assistant"
                required
                maxLength={100}
              />
            </label>
          </div>


          <label>
            <span>
              Description
            </span>

            <textarea
              name="description"
              value={
                form.description
              }
              onChange={
                updateField
              }
              rows={3}
              placeholder={
                "Describe what this assistant is used for."
              }
            />
          </label>


          <label>
            <span>
              System prompt
            </span>

            <textarea
              name="system_prompt"
              value={
                form.system_prompt
              }
              onChange={
                updateField
              }
              rows={6}
              placeholder={
                "Explain how the assistant should behave."
              }
            />
          </label>


          <div className="assistant-form__grid">
            <label>
              <span>
                Tone
              </span>

              <select
                name="tone"
                value={
                  form.tone
                }
                onChange={
                  updateField
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


            <label>
              <span>
                Model
              </span>

              <input
                name="model_name"
                value={
                  form.model_name
                }
                onChange={
                  updateField
                }
                required
              />
            </label>
          </div>


          <label>
            <span>
              Temperature:{" "}
              {form.temperature}
            </span>

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
                updateField
              }
            />
          </label>


          <div className="assistant-form__toggles">
            <label>
              <input
                type="checkbox"
                name="rag_enabled"
                checked={
                  form.rag_enabled
                }
                onChange={
                  updateField
                }
              />

              <span>
                Enable RAG
              </span>
            </label>

            <label>
              <input
                type="checkbox"
                name="is_active"
                checked={
                  form.is_active
                }
                onChange={
                  updateField
                }
              />

              <span>
                Active
              </span>
            </label>
          </div>


          {error && (
            <div className="dashboard-error">
              {error}
            </div>
          )}


          <footer className="dashboard-modal__footer">
            <button
              type="button"
              className="dashboard-secondary-button"
              onClick={
                onClose
              }
              disabled={
                isSaving
              }
            >
              Cancel
            </button>

            <button
              type="submit"
              className="dashboard-primary-button"
              disabled={
                isSaving
              }
            >
              {isSaving
                ? "Saving..."
                : assistant
                  ? "Save changes"
                  : "Create assistant"}
            </button>
          </footer>
        </form>
      </section>
    </div>
  );
}