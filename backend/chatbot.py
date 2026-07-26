import sys

from ai_service import create_chat, create_client, generate_reply


def main() -> None:
    try:
        client = create_client()
        chat = create_chat(client)

        print("Quantheonix AI Chatbot")
        print("Type 'exit' or 'quit' to close the chatbot.\n")

        while True:
            user_message = input("You: ").strip()

            if not user_message:
                print("Please enter a message.\n")
                continue

            if user_message.lower() in {"exit", "quit"}:
                print("AI: Goodbye!")
                break

            reply = generate_reply(chat, user_message)
            print(f"\nAI: {reply}\n")

    except KeyboardInterrupt:
        print("\nAI: Goodbye!")

    except Exception as error:
        print(f"\nError: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()