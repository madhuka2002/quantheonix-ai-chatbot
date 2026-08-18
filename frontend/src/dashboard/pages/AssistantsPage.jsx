import {
  useState,
} from "react";

import {
  createAssistant,
  deleteAssistant,
  updateAssistant,
} from "../../services/assistantApi";

import AssistantFormModal
  from "../components/AssistantFormModal";


export default function AssistantsPage({
  assistants,
  isLoading,
  error,
  onRefresh,
  selectedAssistantId,
  onSelectAssistant,
}) {
  const [
    modalMode,
    setModalMode,
  ] = useState(null);

  const [
    selectedAssistant,
    setSelectedAssistant,
  ] = useState(null);

  const [
    mutationError,
    setMutationError,
  ] = useState("");

  const [
    isSaving,
    setIsSaving,
  ] = useState(false);

  const [
    deletingId,
    setDeletingId,
  ] = useState(null);


  function openCreateModal() {
    setSelectedAssistant(null);
    setMutationError("");
    setModalMode("create");
  }


  function openEditModal(
    assistant,
  ) {
    setSelectedAssistant(
      assistant,
    );

    setMutationError("");
    setModalMode("edit");
  }


  function closeModal() {
    if (isSaving) {
      return;
    }

    setModalMode(null);
    setSelectedAssistant(null);
    setMutationError("");
  }


  async function handleSave(
    formData,
  ) {
    setIsSaving(true);
    setMutationError("");

    try {
      if (
        modalMode === "edit" &&
        selectedAssistant
      ) {
        await updateAssistant(
          selectedAssistant.id,
          formData,
        );
      } else {
        const createPayload = {
          name:
            formData.name,

          display_name:
            formData.display_name,

          description:
            formData.description,

          system_prompt:
            formData.system_prompt,

          tone:
            formData.tone,

          temperature:
            formData.temperature,

          model_name:
            formData.model_name,

          rag_enabled:
            formData.rag_enabled,
        };

        const createdAssistant =
          await createAssistant(
            createPayload,
          );

        if (
          createdAssistant?.id &&
          onSelectAssistant
        ) {
          onSelectAssistant(
            createdAssistant.id,
          );
        }
      }

      await onRefresh();

      setModalMode(null);
      setSelectedAssistant(null);
    } catch (requestError) {
      setMutationError(
        requestError instanceof Error
          ? requestError.message
          : "The assistant could not be saved.",
      );
    } finally {
      setIsSaving(false);
    }
  }


  async function handleDelete(
    assistant,
  ) {
    if (assistant.is_default) {
      return;
    }

    const confirmed =
      window.confirm(
        `Delete "${assistant.display_name}" permanently?`,
      );

    if (!confirmed) {
      return;
    }

    setDeletingId(
      assistant.id,
    );

    setMutationError("");

    try {
      await deleteAssistant(
        assistant.id,
      );

      await onRefresh();
    } catch (requestError) {
      setMutationError(
        requestError instanceof Error
          ? requestError.message
          : "The assistant could not be deleted.",
      );
    } finally {
      setDeletingId(null);
    }
  }


  return (
    <div className="dashboard-page">
      <section className="dashboard-toolbar">
        <div>
          <span className="dashboard-eyebrow">
            Assistant library
          </span>

          <h2>
            Your assistants
          </h2>

          <p>
            Each assistant keeps its
            own AI configuration,
            widget design and allowed
            domains.
          </p>
        </div>

        <button
          type="button"
          className="dashboard-primary-button"
          onClick={
            openCreateModal
          }
        >
          + New assistant
        </button>
      </section>


      {(error || mutationError) && (
        <div className="dashboard-error">
          <span>
            {mutationError || error}
          </span>

          {!mutationError && (
            <button
              type="button"
              onClick={onRefresh}
            >
              Retry
            </button>
          )}
        </div>
      )}


      {isLoading ? (
        <div className="assistant-grid">
          {[1, 2, 3].map(
            (item) => (
              <div
                key={item}
                className="assistant-card assistant-card--loading"
              />
            ),
          )}
        </div>
      ) : (
        <div className="assistant-grid">
          {assistants.map(
            (assistant) => {
              const isSelected =
                selectedAssistantId ===
                assistant.id;

              return (
                <article
                  key={assistant.id}
                  className={
                    isSelected
                      ? "assistant-card assistant-card--selected"
                      : "assistant-card"
                  }
                >
                  <div className="assistant-card__top">
                    <div className="assistant-card__avatar">
                      {assistant.display_name
                        .slice(0, 2)
                        .toUpperCase()}
                    </div>

                    <div className="assistant-card__badges">
                      {assistant.is_default && (
                        <span className="dashboard-badge">
                          Default
                        </span>
                      )}

                      {isSelected && (
                        <span className="dashboard-badge">
                          Selected
                        </span>
                      )}

                      <span
                        className={
                          assistant.is_active
                            ? "dashboard-status dashboard-status--active"
                            : "dashboard-status"
                        }
                      >
                        {assistant.is_active
                          ? "Active"
                          : "Inactive"}
                      </span>
                    </div>
                  </div>


                  <div className="assistant-card__body">
                    <h3>
                      {
                        assistant.display_name
                      }
                    </h3>

                    <span>
                      {assistant.name}
                    </span>

                    <p>
                      {assistant.description ||
                        "No description added yet."}
                    </p>
                  </div>


                  <div className="assistant-card__meta">
                    <div>
                      <span>
                        Tone
                      </span>

                      <strong>
                        {assistant.tone}
                      </strong>
                    </div>

                    <div>
                      <span>
                        Temperature
                      </span>

                      <strong>
                        {
                          assistant.temperature
                        }
                      </strong>
                    </div>

                    <div>
                      <span>
                        RAG
                      </span>

                      <strong>
                        {assistant.rag_enabled
                          ? "On"
                          : "Off"}
                      </strong>
                    </div>
                  </div>


                  <div className="assistant-card__footer assistant-card__footer--actions">
                    <button
                      type="button"
                      className="dashboard-secondary-button"
                      disabled={
                        isSelected
                      }
                      onClick={() =>
                        onSelectAssistant(
                          assistant.id,
                        )
                      }
                    >
                      {isSelected
                        ? "Selected"
                        : "Select"}
                    </button>

                    <button
                      type="button"
                      className="dashboard-secondary-button"
                      onClick={() =>
                        openEditModal(
                          assistant,
                        )
                      }
                    >
                      Configure
                    </button>

                    <button
                      type="button"
                      className="dashboard-danger-button"
                      disabled={
                        assistant.is_default ||
                        deletingId ===
                          assistant.id
                      }
                      title={
                        assistant.is_default
                          ? "The default assistant cannot be deleted."
                          : "Delete assistant"
                      }
                      onClick={() =>
                        handleDelete(
                          assistant,
                        )
                      }
                    >
                      {deletingId ===
                      assistant.id
                        ? "Deleting..."
                        : "Delete"}
                    </button>
                  </div>
                </article>
              );
            },
          )}


          {!assistants.length && (
            <div className="dashboard-empty-state">
              <strong>
                No assistants yet
              </strong>

              <p>
                Create your first AI
                assistant to get
                started.
              </p>

              <button
                type="button"
                className="dashboard-primary-button"
                onClick={
                  openCreateModal
                }
              >
                Create assistant
              </button>
            </div>
          )}
        </div>
      )}


      {modalMode && (
        <AssistantFormModal
          key={
            selectedAssistant?.id ??
            "new-assistant"
          }
          assistant={
            selectedAssistant
          }
          isSaving={isSaving}
          error={mutationError}
          onClose={closeModal}
          onSubmit={handleSave}
        />
      )}
    </div>
  );
}