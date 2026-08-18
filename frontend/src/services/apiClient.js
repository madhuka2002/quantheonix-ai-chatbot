import {
  clearAuthentication,
  getAccessToken,
} from "./authStorage";


export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

export const API_V1_URL =
  `${API_BASE_URL}/api/v1`;


function createApiError(
  message,
  status,
  code = null,
) {
  const error = new Error(message);

  error.status = status;
  error.code = code;

  return error;
}


function extractErrorMessage(
  data,
  fallbackMessage,
) {
  if (
    typeof data?.error?.message === "string"
  ) {
    return data.error.message;
  }

  if (
    typeof data?.detail === "string"
  ) {
    return data.detail;
  }

  if (Array.isArray(data?.detail)) {
    return data.detail
      .map((item) => item?.msg)
      .filter(Boolean)
      .join(", ");
  }

  return fallbackMessage;
}


async function parseResponse(
  response,
) {
  if (response.status === 204) {
    return null;
  }

  const contentType =
    response.headers.get("content-type") || "";

  if (
    !contentType.includes(
      "application/json",
    )
  ) {
    return null;
  }

  try {
    return await response.json();
  } catch {
    return null;
  }
}


export function createAuthenticatedHeaders(
  additionalHeaders = {},
) {
  const token = getAccessToken();

  if (!token) {
    throw createApiError(
      "Your login session has expired.",
      401,
    );
  }

  return {
    Accept: "application/json",
    Authorization: `Bearer ${token}`,
    ...additionalHeaders,
  };
}


export async function apiRequest(
  path,
  {
    method = "GET",
    body,
    headers = {},
    signal,
    fallbackMessage =
      "The request could not be completed.",
  } = {},
) {
  let response;

  const requestHeaders =
    createAuthenticatedHeaders(
      body !== undefined
        ? {
            "Content-Type":
              "application/json",
            ...headers,
          }
        : headers,
    );

  try {
    response = await fetch(
      `${API_V1_URL}${path}`,
      {
        method,
        headers: requestHeaders,
        body:
          body !== undefined
            ? JSON.stringify(body)
            : undefined,
        signal,
      },
    );
  } catch (error) {
    if (error?.name === "AbortError") {
      throw error;
    }

    throw new Error(
      "Unable to connect to the Quantheonix server.",
      {
        cause: error,
      },
    );
  }

  const data = await parseResponse(
    response,
  );

  if (response.status === 401) {
    clearAuthentication();
  }

  if (!response.ok) {
    throw createApiError(
      extractErrorMessage(
        data,
        fallbackMessage,
      ),
      response.status,
      data?.error?.code ?? null,
    );
  }

  return data;
}