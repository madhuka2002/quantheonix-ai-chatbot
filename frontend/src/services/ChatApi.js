const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


async function parseResponse(response) {
  try {
    return await response.json();
  } catch {
    throw new Error(
      "The server returned an invalid response.",
    );
  }
}


export async function sendChatMessage(
  message,
  conversationId = null,
) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },

      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });
  } catch {
    throw new Error(
      "Unable to connect to the chatbot server.",
    );
  }

  const data = await parseResponse(response);

  if (!response.ok) {
    if (response.status === 429) {
      throw new Error(
        "Too many messages were sent. Please wait a moment and try again.",
      );
    }

    throw new Error(
      data.detail || "The chatbot request failed.",
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
      `${API_BASE_URL}/api/conversations/${conversationId}`,
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
    throw new Error(
      data.detail ||
        "The conversation could not be reset.",
    );
  }

  return data;
}