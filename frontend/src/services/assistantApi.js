import {
  apiRequest,
} from "./apiClient";


export function listAssistants() {
  return apiRequest(
    "/assistants",
    {
      fallbackMessage:
        "Your assistants could not be loaded.",
    },
  );
}


export function getAssistant(
  assistantId,
) {
  return apiRequest(
    `/assistants/${encodeURIComponent(
      assistantId,
    )}`,
    {
      fallbackMessage:
        "The assistant could not be loaded.",
    },
  );
}


export function createAssistant(
  assistant,
) {
  return apiRequest(
    "/assistants",
    {
      method: "POST",
      body: assistant,
      fallbackMessage:
        "The assistant could not be created.",
    },
  );
}


export function updateAssistant(
  assistantId,
  updates,
) {
  return apiRequest(
    `/assistants/${encodeURIComponent(
      assistantId,
    )}`,
    {
      method: "PATCH",
      body: updates,
      fallbackMessage:
        "The assistant could not be updated.",
    },
  );
}


export function deleteAssistant(
  assistantId,
) {
  return apiRequest(
    `/assistants/${encodeURIComponent(
      assistantId,
    )}`,
    {
      method: "DELETE",
      fallbackMessage:
        "The assistant could not be deleted.",
    },
  );
}