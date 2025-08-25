import os
import re
import time
import asyncio
from ChatbotService.multimodal_chatbot import GeminiMultimodalChatbot


def extract_image_paths(text):
    potential_paths = re.findall(r'[\w./\\-]+\.(?:png|jpg|jpeg|gif|webp)', text, flags=re.IGNORECASE)
    return [p for p in potential_paths if os.path.isfile(p)]


def stream_print(text, delay=0.02):
    """Stream characters like typing effect"""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  


async def run_chatbot(chatbot, prompt, images=None):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, chatbot.get_response, prompt, images)


async def process_query(chatbot, user_input, images, system_instruction):
    # Run chatbot
    chatbot_response = await run_chatbot(chatbot, user_input, images)
    return chatbot_response["response"] if chatbot_response.get("success") else "⚠️ Chatbot failed."


def main():
    print("🌍 Recycling & Sustainability Assistant")
    print("=" * 60)

    chatbot = GeminiMultimodalChatbot()

    system_instruction = """
    You are a Recycling & Sustainability Assistant.
    Answer with factual recycling and sustainability insights 
    in a friendly conversational tone.
    """

    print("\nType 'quit' to exit\n")

    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            if not user_input:
                continue

            images = extract_image_paths(user_input)

            final_response = asyncio.run(
                process_query(chatbot, user_input, images, system_instruction)
            )
            print(f"\n🤖 Assistant: {final_response}")

        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
