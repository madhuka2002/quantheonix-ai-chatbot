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
  code = null,
) {
  const error = new Error(message);
  error.status = status;
  error.code = code;

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

async function consumeNdjsonStream({
  response,
  conversationId = null,
  onStart,
  onChunk,
  onDone,
}) {
  if (response.status === 401) {
    clearAuthentication();
  }

  if (!response.ok) {
    let responseData = null;

    try {
      responseData = await response.json();
    } catch {
      // The response may not contain JSON.
    }

    throw createApiError(
      extractApiErrorMessage(
        responseData,
        "The streaming request failed.",
      ),
      response.status,
      responseData?.error?.code ?? null,
    );
  }

  if (!response.body) {
    throw new Error(
      "The browser could not read the response stream.",
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";
  let finalConversationId =
    conversationId;

  function processEvent(event) {
    if (event.type === "start") {
      finalConversationId =
        event.conversation_id ??
        finalConversationId;

      onStart?.(event);
      return;
    }

    if (event.type === "chunk") {
      onChunk?.(
        event.text ?? "",
        event,
      );

      return;
    }

    if (event.type === "done") {
      finalConversationId =
        event.conversation_id ??
        finalConversationId;

      onDone?.(event);
      return;
    }

    if (event.type === "error") {
      throw createApiError(
        event.message ||
          "The chatbot could not complete the request.",
        500,
        event.code ?? null,
      );
    }
  }

  try {
    while (true) {
      const {
        value,
        done,
      } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(
        value,
        {
          stream: true,
        },
      );

      const lines = buffer.split("\n");

      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const cleanedLine =
          line.trim();

        if (!cleanedLine) {
          continue;
        }

        let event;

        try {
          event = JSON.parse(
            cleanedLine,
          );
        } catch (error) {
          throw new Error(
            "The chatbot returned an invalid stream event.",
            {
              cause: error,
            },
          );
        }

        processEvent(event);
      }
    }

    buffer += decoder.decode();

    const remainingLine =
      buffer.trim();

    if (remainingLine) {
      let event;

      try {
        event = JSON.parse(
          remainingLine,
        );
      } catch (error) {
        throw new Error(
          "The chatbot returned an invalid final stream event.",
          {
            cause: error,
          },
        );
      }

      processEvent(event);
    }

    return {
      conversationId:
        finalConversationId,
    };
  } finally {
    reader.releaseLock();
  }
}

export async function streamChatMessage({
  message,
  conversationId = null,
  signal,
  onStart,
  onChunk,
  onDone,
}) {
  let response;

  try {
    response = await fetch(
      `${API_V1_URL}/chat/stream`,
      {
        method: "POST",
        headers: createAuthenticatedHeaders({
          Accept: "application/x-ndjson",
          "Content-Type": "application/json",
        }),
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        }),
        signal,
      },
    );
  } catch (error) {
    if (error?.name === "AbortError") {
      throw error;
    }

    throw new Error(
      "Unable to connect to the chatbot server.",
      {
        cause: error,
      },
    );
  }

  return consumeNdjsonStream({
    response,
    conversationId,
    onStart,
    onChunk,
    onDone,
  });
}

export async function regenerateChatMessage({
  conversationId,
  signal,
  onStart,
  onChunk,
  onDone,
}) {
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
      )}/regenerate`,
      {
        method: "POST",
        headers: createAuthenticatedHeaders({
          Accept:
            "application/x-ndjson",
        }),
        signal,
      },
    );
  } catch (error) {
    if (error?.name === "AbortError") {
      throw error;
    }

    throw new Error(
      "Unable to connect to the chatbot server.",
      {
        cause: error,
      },
    );
  }

  return consumeNdjsonStream({
    response,
    conversationId,
    onStart,
    onChunk,
    onDone,
  });
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

export async function renameConversation(
  conversationId,
  title,
) {
  let response;

  try {
    response = await fetch(
      `${API_V1_URL}/conversations/${encodeURIComponent(
        conversationId,
      )}`,
      {
        method: "PATCH",
        headers: createAuthenticatedHeaders({
          "Content-Type": "application/json",
        }),
        body: JSON.stringify({
          title,
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
    throw createApiError(
      extractApiErrorMessage(
        data,
        "The conversation could not be renamed.",
      ),
      response.status,
      data?.error?.code ?? null,
    );
  }

  return data;
}

export async function listConversations({
  limit = 50,
  offset = 0,
  search = "",
} = {}) {
  const query = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  const cleanedSearch = search.trim();

  if (cleanedSearch) {
    query.set(
      "search",
      cleanedSearch,
    );
  }

  let response;

  try {
    response = await fetch(
      `${API_V1_URL}/conversations?${query.toString()}`,
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
    throw createApiError(
      extractApiErrorMessage(
        data,
        "The conversations could not be loaded.",
      ),
      response.status,
      data?.error?.code ?? null,
    );
  }

  return data;
}

