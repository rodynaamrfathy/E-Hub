import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, List, Optional
import logging
import tempfile
import os
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
from services.conversation.GeminiMultimodalChatbot import GeminiMultimodalChatbot

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
async def send_message_stream_with_images(
    conv_id: str,
    content: str = Form(..., description="Message content"),
    images: Optional[List[UploadFile]] = File(None, description="Optional image files"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Send user message with optional images and stream assistant response (SSE).
    """
    temp_files = []
    image_paths = []

    try:
        if not content.strip() and not images:
            raise HTTPException(status_code=400, detail="Message content or images required")

        # Save uploaded images to temp files
        if images:
            for img in images:
                suffix = os.path.splitext(img.filename)[-1] or ".jpg"
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp.write(await img.read())
                tmp.flush()
                tmp.close()
                temp_files.append(tmp.name)
                image_paths.append(tmp.name)

        # Init chatbot for this conversation
        chatbot = GeminiMultimodalChatbot(session_id=conv_id)

        # Message service
        msg_service = MessageService()

        # Save user message in DB
        user_msg = await msg_service.create_message(
            db, conv_id, sender="user", content=content
        )

        async def event_generator() -> AsyncGenerator[str, None]:
            try:
                logger.info(f"🔹 Starting stream for conv={conv_id}, content={content[:80]}...")
                if image_paths:
                    logger.info(f"Processing {len(image_paths)} images: {image_paths}")

                full_response_tokens = []

                # Stream from chatbot
                async for token in chatbot.stream_response(content, image_paths if image_paths else None):
                    full_response_tokens.append(token.strip())
                    yield f"data: {json.dumps({'token': token})}\n\n"
                    await asyncio.sleep(0)

                # Get full response (from chatbot memory or tokens)
                full_response = chatbot.get_full_response() or " ".join(full_response_tokens).strip()

                if full_response:
                    ai_msg = await msg_service.create_message(
                        db, conv_id, sender="assistant", content=full_response
                    )
                    logger.info(f"💬 Saved assistant response: {full_response[:80]}...")

                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"⚠️ Streaming error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            finally:
                # Clean up temp files
                for path in temp_files:
                    try:
                        if os.path.exists(path):
                            os.unlink(path)
                    except:
                        pass

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            },
        )

    except Exception as e:
        # Cleanup on failure
        for path in temp_files:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except:
                pass
        logger.error(f"Unexpected error in send_message_stream_with_images: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
