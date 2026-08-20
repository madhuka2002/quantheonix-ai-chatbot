import {
  useEffect,
  useState,
} from "react";

import ChatWidget from "./ChatWidget";

import {
  getPublicAssistantConfig,
} from "./chatApi";


function QuantheonixChat({
  apiUrl,
  assistantId,
}) {
  const [config, setConfig] =
    useState(null);

  const [error, setError] =
    useState("");

  useEffect(() => {
    const abortController =
      new AbortController();

    async function loadConfig() {
      try {
        setError("");

        const data =
          await getPublicAssistantConfig({
            apiUrl,
            assistantId,
            signal:
              abortController.signal,
          });

        setConfig(data);
      } catch (requestError) {
        if (
          requestError?.name ===
          "AbortError"
        ) {
          return;
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load the assistant.",
        );
      }
    }

    loadConfig();

    return () => {
      abortController.abort();
    };
  }, [
    apiUrl,
    assistantId,
  ]);

  if (error) {
    console.error(
      "[QuantheonixChat]",
      error,
    );

    return null;
  }

  if (!config) {
    return null;
  }

  return (
    <ChatWidget
      apiUrl={apiUrl}
      assistantId={assistantId}
      title={
        config.display_name ||
        "AI Assistant"
      }
      settings={
        config.widget || {}
      }
    />
  );
}


export default QuantheonixChat;