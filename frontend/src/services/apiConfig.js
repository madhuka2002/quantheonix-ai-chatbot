const configuredApiBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.trim();

const browserOrigin =
  typeof window === "undefined"
    ? ""
    : window.location.origin;

export const API_BASE_URL =
  configuredApiBaseUrl?.replace(/\/+$/, "") ||
  browserOrigin;

export const API_V1_URL =
  `${API_BASE_URL}/api/v1`;
