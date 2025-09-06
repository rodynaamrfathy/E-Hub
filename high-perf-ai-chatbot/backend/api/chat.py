import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, List
import logging
from services.db.postgres import get_db_session
from services.dto import (
    ConversationCreateDTO,
    ConversationResponseDTO,
    ConversationListDTO,
    MessageCreateDTO,
    MessageResponseDTO,
    MessageHistoryDTO,
)
from services.repositories.conversation_service import ConversationService
from services.repositories.message_service import MessageService
from services.repositories.history_service import get_conversation_history
from services.conversation.multimodal_chatbot import GeminiMultimodalChatbot

router = APIRouter(tags=["Chat"])
logger = logging.getLogger(__name__)


@router.post("/new", response_model=ConversationResponseDTO)
async def create_conversation(
    payload: ConversationCreateDTO,
    db: AsyncSession = Depends(get_db_session)
):
    """Start a new conversation"""
    service = ConversationService()
    conversation = await service.create_conversation(db, user_id="default", title=payload.title)
    return ConversationResponseDTO(
        conv_id=conversation.conv_id,
        title=conversation.title,
        created_at=conversation.created_at
    )


@router.get("/list", response_model=List[ConversationListDTO])
async def list_conversations(
    db: AsyncSession = Depends(get_db_session)
):
    """List all conversations"""
    service = ConversationService()
    conversations = await service.list_conversations(db, user_id="default")
    return [
        ConversationListDTO(
            conv_id=conv.conv_id,
            title=conv.title,
            updated_at=conv.updated_at
        )
        for conv in conversations
    ]


@router.delete("/{conv_id}")
async def delete_conversation(
    conv_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a conversation"""
    service = ConversationService()
    success = await service.delete_conversation(db, conv_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": f"Conversation {conv_id} deleted"}



@router.get("/{conv_id}/history", response_model=List[MessageHistoryDTO])
async def conversation_history(
    conv_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all messages in a conversation"""
    history = await get_conversation_history(db, conv_id)
    return history


@router.post("/{conv_id}/send-stream")
async def send_message_stream(
    conv_id: str,
    payload: MessageCreateDTO,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Send user message and stream assistant response (SSE).
    """
    msg_service = MessageService()
    chatbot = GeminiMultimodalChatbot()

    # Save user message
    user_msg = await msg_service.create_message(
        db, conv_id, sender="user", content=payload.content
    )

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            print(f"Starting stream for conversation {conv_id} with content: {payload.content}")
            # Stream tokens from chatbot
            async for token in chatbot.stream_response(payload.content):
                print(f"Streaming token: {token}")
                # yield token as SSE event
                yield f"data: {json.dumps({'token': token})}\n\n"
                await asyncio.sleep(0)  # let event loop breathe

            # Save assistant full reply
            reply_text = chatbot.get_full_response()
            ai_msg = await msg_service.create_message(
                db, conv_id, sender="assistant", content=reply_text
            )

            # Notify client that streaming is done
            print("Streaming completed, sending [DONE]")
            yield f"data: [DONE]\n\n"

        except Exception as e:
            print(f"Error in streaming: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )