import ChatWidget from "./ChatWidget";


function QuantheonixChat({
  apiUrl,
  accessToken = null,
  getAccessToken = null,
  title = "Quantheonix AI",
  welcomeMessage =
    "Hello! How can I help you?",
  placeholder =
    "Type your message...",
  initiallyOpen = false,
  position = "bottom-right",
}) {
  return (
    <ChatWidget
      apiUrl={apiUrl}
      accessToken={accessToken}
      getAccessToken={getAccessToken}
      title={title}
      welcomeMessage={welcomeMessage}
      placeholder={placeholder}
      initiallyOpen={initiallyOpen}
      position={position}
    />
  );
}


export default QuantheonixChat;