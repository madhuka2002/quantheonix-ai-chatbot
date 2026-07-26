const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

/**
 * Send a message to the FastAPI chatbot.
 *
 * @param {string} message
 * @param {string | null} conversationId
 * @returns {Promise<{conversation_id: string, reply: string}>}
 */
export async function sendChatMessage(message, conversationId = null) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
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

    let data;

    try {
        data = await response.json();
    } catch {
        throw new Error("The server returned an invalid response.");
    }

    if (!response.ok) {
        throw new Error(
            data.detail || "The chatbot request failed.",
        );
    }

    return data;
}