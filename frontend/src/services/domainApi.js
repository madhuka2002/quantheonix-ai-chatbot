import {
  apiRequest,
} from "./apiClient";


export function listDomains(
  assistantId,
) {
  return apiRequest(
    `/assistants/${encodeURIComponent(
      assistantId,
    )}/domains`,
    {
      fallbackMessage:
        "Allowed domains could not be loaded.",
    },
  );
}


export function addDomain(
  assistantId,
  domain,
) {
  return apiRequest(
    `/assistants/${encodeURIComponent(
      assistantId,
    )}/domains`,
    {
      method: "POST",
      body: {
        domain,
      },
      fallbackMessage:
        "The domain could not be added.",
    },
  );
}


export function deleteDomain(
  assistantId,
  domainId,
) {
  return apiRequest(
    `/assistants/${encodeURIComponent(
      assistantId,
    )}/domains/${encodeURIComponent(
      domainId,
    )}`,
    {
      method: "DELETE",
      fallbackMessage:
        "The domain could not be removed.",
    },
  );
}