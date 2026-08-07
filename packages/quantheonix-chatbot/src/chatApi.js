function createApiError(
  message,
  status = 500,
  code = null,
) {
  const error = new Error(message);

  error.status = status;
  error.code = code;

  return error;
}


async function resolveAccessToken({
  accessToken,
  getAccessToken,
}) {
  if (
    typeof getAccessToken ===
    "function"
  ) {
    return (
      await getAccessToken()
    );
  }

  return accessToken;
}


async function consumeNdjsonStream({
  response,
  onStart,
  onChunk,
  onDone,
}) {
  if (!response.ok) {
    let data = null;

    try {
      data = await response.json();
    } catch {
      // The server may not return JSON.
    }

    throw createApiError(
      data?.error?.message ||
        data?.detail ||
        "The chatbot request failed.",
      response.status,
      data?.error?.code ?? null,
    );
  }

  if (!response.body) {
    throw new Error(
      "Streaming responses are not supported in this browser.",
    );
  }

  const reader =
    response.body.getReader();

  const decoder =
    new TextDecoder();

  let buffer = "";
  let conversationId = null;

  function processEvent(event) {
    if (event.type === "start") {
      conversationId =
        event.conversation_id ??
        conversationId;

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
      conversationId =
        event.conversation_id ??
        conversationId;

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

      const lines =
        buffer.split("\n");

      buffer =
        lines.pop() ?? "";

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
      processEvent(
        JSON.parse(
          remainingLine,
        ),
      );
    }

    return {
      conversationId,
    };
  } finally {
    reader.releaseLock();
  }
}


export async function streamWidgetMessage({
  apiUrl,
  accessToken,
  getAccessToken,
  message,
  conversationId = null,
  signal,
  onStart,
  onChunk,
  onDone,
}) {
  if (!apiUrl) {
    throw new Error(
      "The chatbot API URL is required.",
    );
  }

  const token =
    await resolveAccessToken({
      accessToken,
      getAccessToken,
    });

  const headers = {
    Accept:
      "application/x-ndjson",
    "Content-Type":
      "application/json",
  };

  if (token) {
    headers.Authorization =
      `Bearer ${token}`;
  }

  let response;

  try {
    response = await fetch(
      `${apiUrl.replace(/\/$/, "")}/api/v1/chat/stream`,
      {
        method: "POST",
        headers,
        body: JSON.stringify({
          message,
          conversation_id:
            conversationId,
        }),
        signal,
      },
    );
  } catch (error) {
    if (
      error?.name ===
      "AbortError"
    ) {
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
    onStart,
    onChunk,
    onDone,
  });
}