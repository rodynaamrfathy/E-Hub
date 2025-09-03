from fastapi import WebSocket
from services.conversation.multimodal_chatbot import GeminiMultimodalChatbot
import json
from typing import List, Dict, Optional

async def stream_gemini_to_websocket(websocket: WebSocket, payload: str):
    """
    Handles a chat message with optional images entirely in memory.
    Expects payload JSON:
    {
        "text": "Hello",
        "images": [
            {"mime_type": "image/png", "image_base64": "..."},
            ...
        ]
    }
    """
    chatbot = GeminiMultimodalChatbot()
    
    # Defaults
    text: str = payload
    images: Optional[List[Dict[str, str]]] = None

    # Try to parse JSON payload
    try:
        data = json.loads(payload)
        if isinstance(data, dict):
            text = data.get("text", "")
            images = data.get("images")  # list of {"mime_type", "image_base64"}
    except Exception:
        # Keep defaults if parsing fails
        pass

    try:
        # Send text + images to chatbot asynchronously
        result = await chatbot.get_response_async(text, images)

        # Send response back to client
        if result.get("success"):
            await websocket.send_text(json.dumps(result))
        else:
            await websocket.send_text(json.dumps({
                "success": False,
                "error": result.get("error", "Unknown error")
            }))

        # Notify client that processing is done
        await websocket.send_text("[DONE]")
        
    except Exception as e:
        # Catch any unexpected errors
        await websocket.send_text(json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }))

