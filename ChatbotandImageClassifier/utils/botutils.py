from fastapi import FastAPI, Form, UploadFile, File
import asyncio
from ChatbotService.multimodal_chatbot import GeminiMultimodalChatbot
from agents.waste_mangment_agent.core.agent import WasteManagementAgent


# ----------------------------
# Utility functions
# ----------------------------
async def run_agent(agent, query: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, agent.process_query, query)

async def run_chatbot(chatbot, prompt: str, images=None):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, chatbot.get_response, prompt, images)

async def process_query(chatbot, agent, user_input: str, images, system_instruction: str):
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

