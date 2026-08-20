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


function normalizeApiUrl(apiUrl) {
  if (!apiUrl) {
    throw new Error(
      "The chatbot API URL is required.",
    );
  }

  return apiUrl.replace(/\/$/, "");
}


export async function getPublicAssistantConfig({
  apiUrl,
  assistantId,
  signal,
}) {
  if (!assistantId) {
    throw new Error(
      "The assistant ID is required.",
    );
  }

  const baseUrl =
    normalizeApiUrl(apiUrl);

  const endpoint =
    `${baseUrl}/api/v1/public/assistants/` +
    `${encodeURIComponent(assistantId)}/config`;

  let response;

  try {
    response = await fetch(
      endpoint,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
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

  if (!response.ok) {
    let data = null;

    try {
      data = await response.json();
    } catch {
      // Response may not contain JSON.
    }

    throw createApiError(
      data?.error?.message ||
        data?.detail ||
        "Unable to load the assistant.",
      response.status,
      data?.error?.code ?? null,
    );
  }

  return response.json();
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
      const text =
        await response.text();

      if (text) {
        const firstLine =
          text
            .split("\n")
            .find(
              (line) => line.trim(),
            );

        if (firstLine) {
          data = JSON.parse(firstLine);
        }
      }
    } catch {
      // The server may not return valid JSON.
    }

    throw createApiError(
      data?.error?.message ||
        data?.message ||
        "The chatbot request failed.",
      response.status,
      data?.error?.code ??
        data?.code ??
        null,
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
      try {
        processEvent(
          JSON.parse(
            remainingLine,
          ),
        );
      } catch (error) {
        if (
          error?.status ||
          error?.code
        ) {
          throw error;
        }

        throw new Error(
          "The chatbot returned an invalid stream event.",
          {
            cause: error,
          },
        );
      }
    }

    return {
      conversationId,
    };
  } finally {
    reader.releaseLock();
  }
}


export async function streamPublicMessage({
  apiUrl,
  assistantId,
  message,
  conversationId = null,
  signal,
  onStart,
  onChunk,
  onDone,
}) {
  if (!assistantId) {
    throw new Error(
      "The assistant ID is required.",
    );
  }

  const baseUrl =
    normalizeApiUrl(apiUrl);

  const endpoint =
    `${baseUrl}/api/v1/public/chat/stream`;

  let response;

  try {
    response = await fetch(
      endpoint,
      {
        method: "POST",
        headers: {
          Accept:
            "application/x-ndjson",
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          assistant_id: assistantId,
          conversation_id:
            conversationId,
          message,
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
    onStart,
    onChunk,
    onDone,
  });
}