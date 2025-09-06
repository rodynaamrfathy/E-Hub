from fastapi import WebSocket, WebSocketDisconnect
from services.conversation.multimodal_chatbot import GeminiMultimodalChatbot
from pydantic import BaseModel, ValidationError
from typing import List, Optional
import json


class ImagePayload(BaseModel):
    mime_type: str
    image_base64: str


class ChatPayload(BaseModel):
    text: str
    images: List[ImagePayload] = []


async def stream_gemini_to_websocket(websocket: WebSocket, payload: str):
    """
    Handles a chat message with optional images entirely in memory.
    Expects payload JSON matching ChatPayload schema.
    """
    chatbot = GeminiMultimodalChatbot()

    try:
        # ✅ Validate JSON against ChatPayload
        chat_payload = ChatPayload.model_validate_json(payload)

        text = chat_payload.text
        images = [img.model_dump() for img in chat_payload.images]

    except ValidationError as ve:
        await websocket.send_text(json.dumps({
            "success": False,
            "error": f"Invalid payload: {ve.errors()}"
        }))
        return

    try:
        # ✅ Send text + images to chatbot asynchronously
        result = await chatbot.get_response_async(text, images)

        # ✅ Send response back
        await websocket.send_text(json.dumps(result if result.get("success") else {
            "success": False,
            "error": result.get("error", "Unknown error")
        }))

        # ✅ End-of-response marker
        await websocket.send_text("[DONE]")

    except Exception as e:
        await websocket.send_text(json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }))
