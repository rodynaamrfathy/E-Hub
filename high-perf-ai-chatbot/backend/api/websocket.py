from fastapi import WebSocket
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

async def stream_gemini_to_websocket(websocket: WebSocket, query: str):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=google_api_key,
    )
    try:
        async for chunk in llm.astream(query):
            if chunk.content:
                await websocket.send_text(chunk.content)
    except Exception as e:
        print(f"[ERROR] {e}")
