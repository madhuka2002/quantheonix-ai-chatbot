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

        headers: {
          "Content-Type":
            "application/json",
          Accept: "application/json",
        },

        body: JSON.stringify({
          message,
          conversation_id:
            conversationId,
        }),
      },
    );
  } catch {
    throw new Error(
      "Unable to connect to the chatbot server.",
    );
  }

  const data = await parseResponse(response);

  if (!response.ok) {
    if (response.status === 429) {
      throw new Error(
        "Too many requests. Please wait a moment and try again.",
      );
    }

    const errorMessage =
      extractApiErrorMessage(
        data,
        "The chatbot request failed.",
      );

    throw new Error(errorMessage);
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
      `${API_V1_URL}/conversations/${conversationId}`,
      {
        method: "DELETE",

        headers: {
          Accept: "application/json",
        },
      },
    );
  } catch {
    throw new Error(
      "Unable to connect to the chatbot server.",
    );
  }

  const data = await parseResponse(response);

  if (!response.ok) {
    const errorMessage =
      extractApiErrorMessage(
        data,
        "The conversation could not be reset.",
      );

    throw new Error(errorMessage);
  }

  return data;
}