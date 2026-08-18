import {
  apiRequest,
} from "./apiClient";


export function getWidgetSettings(
  assistantId,
) {
  return apiRequest(
    `/assistants/${encodeURIComponent(
      assistantId,
    )}/widget`,
    {
      fallbackMessage:
        "Widget settings could not be loaded.",
    },
  );
}


export function updateWidgetSettings(
  assistantId,
  updates,
) {
  return apiRequest(
    `/assistants/${encodeURIComponent(
      assistantId,
    )}/widget`,
    {
      method: "PATCH",
      body: updates,
      fallbackMessage:
        "Widget settings could not be saved.",
    },
  );
}