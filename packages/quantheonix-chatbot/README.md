# Quantheonix Chatbot

An embeddable React AI chatbot widget with:

- 🚀 Streaming responses
- 📝 Markdown rendering
- 💻 Syntax highlighting
- 🔒 JWT authentication support
- 🎨 Customizable theme
- 📱 Responsive design

## Installation

```bash
npm install @quantheonix/chatbot
```

## Basic Usage

```jsx
import { QuantheonixChat } from "@quantheonix/chatbot";

function App() {
  return (
    <QuantheonixChat
      apiUrl="https://your-api.com"
      accessToken="YOUR_TOKEN"
    />
  );
}
```

## Props

| Prop | Type | Description |
|------|------|-------------|
| apiUrl | string | Backend API URL |
| accessToken | string | JWT access token |
| getAccessToken | function | Callback to retrieve a token |
| title | string | Widget title |
| welcomeMessage | string | Initial assistant message |
| placeholder | string | Input placeholder |
| initiallyOpen | boolean | Open widget on page load |
| position | string | `bottom-right` or `bottom-left` |

## License

MIT