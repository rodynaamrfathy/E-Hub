import os
import re
import time

import asyncio
from ChatbotService.multimodal_chatbot import GeminiMultimodalChatbot
from agents.waste_mangment_agent.core.agent import WasteManagementAgent

def extract_image_paths(text):
    potential_paths = re.findall(r'[\w./\\-]+\.(?:png|jpg|jpeg|gif|webp)', text, flags=re.IGNORECASE)
    return [p for p in potential_paths if os.path.isfile(p)]



def stream_print(text, delay=0.02):
    """Stream characters like typing effect"""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  

async def run_agent(agent, query: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, agent.process_query, query)


async def run_chatbot(chatbot, prompt, images=None):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, chatbot.get_response, prompt, images)

async def process_query_option1(chatbot, agent, user_input, images, system_instruction):
    # Run chatbot + agent in parallel
    agent_task = asyncio.create_task(run_agent(agent, user_input))
    chatbot_task = asyncio.create_task(run_chatbot(chatbot, user_input, images))
    agent_response, chatbot_response = await asyncio.gather(agent_task, chatbot_task)

    chatbot_text = chatbot_response["response"] if chatbot_response.get("success") else "⚠️ Chatbot failed."

    merge_prompt = f"""
    {system_instruction}

    User said: "{user_input}"
    Chatbot draft: "{chatbot_text}"
    Agent insight: "{agent_response}"

    Please rewrite as one natural, conversational answer.
    """
    merged = await run_chatbot(chatbot, merge_prompt)
    return merged["response"] if merged.get("success") else f"{chatbot_text}\n\n🌱 Agent: {agent_response}"


async def process_query_option2(chatbot, agent, user_input, images):
    # Start agent in background
    agent_task = asyncio.create_task(run_agent(agent, user_input))

    # Chatbot responds instantly
    chatbot_response = await run_chatbot(chatbot, user_input, images)
    chatbot_text = chatbot_response["response"] if chatbot_response.get("success") else "⚠️ Chatbot failed."
    
    print("\n🤖 Assistant: ", end="", flush=True)
    stream_print(chatbot_text, delay=0.02)

    # Later: agent result streams in
    agent_response = await agent_task
    print("\n🌱 Agent Insight: ", end="", flush=True)
    stream_print(agent_response, delay=0.01)


def main():
    print("🌍 Recycling & Sustainability Assistant (Parallel Modes)")
    print("=" * 60)

    chatbot = GeminiMultimodalChatbot()
    agent = WasteManagementAgent(region="egypt")

    system_instruction = """
    You are a Recycling & Sustainability Assistant.
    - Combine factual insights from the WasteManagementAgent with a friendly conversational tone.
    - Encourage eco-friendly actions.
    """

    print("\nType 'quit' to exit\n")
    mode = input("Choose mode: [1] Merge (polished answer) [2] Two-phase streaming (fastest) → ").strip()

    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            if not user_input:
                continue

            images = extract_image_paths(user_input)

            if mode == "1":
                # Option 1: chatbot rewrites agent’s response
                final_response = asyncio.run(
                    process_query_option1(chatbot, agent, user_input, images, system_instruction)
                )
                print(f"\n🤖 Assistant: {final_response}")
            else:
                # Option 2: fast streaming two-phase response
                asyncio.run(process_query_option2(chatbot, agent, user_input, images))

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
if __name__ == "__main__":
    main()