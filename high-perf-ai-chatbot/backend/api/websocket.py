
# import os
# from fastapi import WebSocket
# from dotenv import load_dotenv

# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# from langchain_mcp_adapters.tools import load_mcp_tools
# from langgraph.prebuilt import create_react_agent
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.messages import AIMessage


# load_dotenv()
# google_api_key = os.getenv("GOOGLE_API_KEY")

# async def stream_gemini_to_websocket(websocket: WebSocket, query: str):
#     server_params = StdioServerParameters(
#         command="python",
#         args=["-m", "services.mcp.server"],  # ✅ package import, not file path
#     )

#     try:
#         # Start MCP client session
#         async with stdio_client(server_params) as (read, write):
#             async with ClientSession(read, write) as session:
#                 await session.initialize()

#                 # Load tools from MCP server
#                 tools = await load_mcp_tools(session)

#                 # Create Gemini LLM
#                 llm = ChatGoogleGenerativeAI(
#                     model="gemini-2.5-pro",
#                     google_api_key=google_api_key,
#                 )

#                 # Create MCP-powered agent
#                 agent = create_react_agent(llm, tools)

#                 # Stream results back to WebSocket

#                 async for chunk in agent.astream({"messages": query}):
#                     if isinstance(chunk, AIMessage):
#                         await websocket.send_text(chunk.content)
#                     else:
#                         # Optional: handle tool calls or other messages
#                         pass


#     except Exception as e:
#         print(f"[ERROR] {e}")
#         await websocket.send_text("⚠️ Error while processing your request.")


from fastapi import WebSocket
from services.conversation.multimodal_chatbot import GeminiMultimodalChatbot
import asyncio
import json

async def stream_gemini_to_websocket(websocket: WebSocket, payload: str):
    chatbot = GeminiMultimodalChatbot()

    # Default values
    text = payload
    images = None

    # Try to parse JSON payload: {"text": str, "images": [{"data": str, "mime_type": str}]}
    try:
        data = json.loads(payload)
        if isinstance(data, dict):
            text = data.get("text", "")
            images = data.get("images")
    except Exception:
        # Not JSON; treat as plain text
        pass

    try:
        # Start getting the response asynchronously
        response_task = asyncio.create_task(chatbot.get_response_async(text, images))

        # Optional: you can yield partial responses here if your chatbot supports streaming
        while not response_task.done():
            await asyncio.sleep(0.1)  # small delay
            # You could send partial text here if available

        # Once complete, send the full response
        result = await response_task
        if result.get("success"):
            await websocket.send_text(result.get("response", ""))
        else:
            await websocket.send_text(f"⚠️ Error: {result.get('error')}")

    except Exception as e:
        print(f"[ERROR] {e}")
        await websocket.send_text("⚠️ Unexpected error while processing your request.")
