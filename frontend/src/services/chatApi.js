import {
  clearAuthentication,
  getAccessToken,
} from "./authStorage";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

const API_V1_URL = `${API_BASE_URL}/api/v1`;


async function parseResponse(response) {
  try {
    return await response.json();
  } catch {
    throw new Error(
      "The server returned an invalid response.",
    );
  }
}


function extractApiErrorMessage(
  responseData,
  fallbackMessage,
) {
  if (
    responseData?.error?.message &&
    typeof responseData.error.message === "string"
  ) {
    const requestId =
      responseData.error.request_id;

    return requestId
      ? `${responseData.error.message} (Request ID: ${requestId})`
      : responseData.error.message;
  }

  if (
    typeof responseData?.detail === "string"
  ) {
    return responseData.detail;
  }

  return fallbackMessage;
}


function createApiError(
  message,
  status,
) {
  const error = new Error(message);
  error.status = status;

  return error;
}


function createAuthenticatedHeaders(
  additionalHeaders = {},
) {
  const token = getAccessToken();

  if (!token) {
    const error = new Error(
      "You must log in before using the chatbot.",
    );

    error.status = 401;

    throw error;
  }

  return {
    Accept: "application/json",
    Authorization: `Bearer ${token}`,
    ...additionalHeaders,
  };
}


export async function sendChatMessage(
  message,
  conversationId = null,
) {
  let response;

  try {
    response = await fetch(
      `${API_V1_URL}/chat`,
      {
        method: "POST",
        headers: createAuthenticatedHeaders({
          "Content-Type": "application/json",
          Accept: "application/json",
        }),
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        }),
      },
    );
  } catch {
    throw new Error(
      "Unable to connect to the chatbot server.",
    );
  }

  const data = await parseResponse(response);

  if (response.status === 401) {
    clearAuthentication();
  }

  if (!response.ok) {
    if (response.status === 429) {
      throw createApiError(
        "Too many requests. Please wait a moment and try again.",
        response.status,
      );
    }

    const errorMessage =
      extractApiErrorMessage(
        data,
        "The chatbot request failed.",
      );

    throw createApiError(
      errorMessage,
      response.status,
    );
  }

  return data;
}


export async function getConversation(
  conversationId,
) {
  if (!conversationId) {
    throw new Error(
      "A conversation ID is required.",
    );
  }

  let response;

  try {
    response = await fetch(
      `${API_V1_URL}/conversations/${encodeURIComponent(
        conversationId,
      )}`,
      {
        method: "GET",
        headers: createAuthenticatedHeaders({
          Accept: "application/json",
        }),
      },
    );
  } catch {
    throw new Error(
      "Unable to connect to the chatbot server.",
    );
  }

  const data = await parseResponse(response);

  if (response.status === 401) {
    clearAuthentication();
  }

  if (!response.ok) {
    const errorMessage =
      extractApiErrorMessage(
        data,
        "The conversation could not be loaded.",
      );

    throw createApiError(
      errorMessage,
      response.status,
    );
  }

  return data;
}


export async function resetConversation(
  conversationId,
) {
  if (!conversationId) {
    return null;
  }

  let response;

  try {
    response = await fetch(
      `${API_V1_URL}/conversations/${encodeURIComponent(
        conversationId,
      )}`,
      {
        method: "DELETE",
        headers: createAuthenticatedHeaders({
          Accept: "application/json",
        }),
      },
    );
  } catch {
    throw new Error(
      "Unable to connect to the chatbot server.",
    );
  }

  const data = await parseResponse(response);

  if (response.status === 401) {
    clearAuthentication();
  }

  if (!response.ok) {
    const errorMessage =
      extractApiErrorMessage(
        data,
        "The conversation could not be reset.",
      );

    throw createApiError(
      errorMessage,
      response.status,
    );
  }

  return data;
}

export async function listConversations({
  limit = 50,
  offset = 0,
} = {}) {
  let response;

  try {
    response = await fetch(
      `${API_V1_URL}/conversations?limit=${limit}&offset=${offset}`,
      {
        method: "GET",
        headers: createAuthenticatedHeaders(),
      },
    );
  } catch {
    throw new Error(
      "Unable to connect to the chatbot server.",
    );
  }

  const data = await parseResponse(response);

  if (response.status === 401) {
    clearAuthentication();
  }

  if (!response.ok) {
    const errorMessage =
      extractApiErrorMessage(
        data,
        "The conversations could not be loaded.",
      );

    throw createApiError(
      errorMessage,
      response.status,
    );
  }

  return data;
}