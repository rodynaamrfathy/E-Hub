from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from database import get_db_session
from dto import (
    ConversationCreateDTO,
    ConversationResponseDTO,
    ConversationListDTO,
    MessageCreateDTO,
    MessageResponseDTO,
    MessageHistoryDTO,
)
from services.conversation_service import ConversationService
from services.message_service import MessageService
from services.history_service import get_conversation_history
# from utils.botutils import process_query
# from core.initializers import chatbot, agent

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


@router.post("/{conv_id}/send", response_model=MessageResponseDTO)
async def send_message(
    conv_id: str,
    payload: MessageCreateDTO,
    db: AsyncSession = Depends(get_db_session)
):
    """Send user message, get assistant response"""
    msg_service = MessageService()

    # Save user message
    user_msg = await msg_service.create_message(db, conv_id, sender="user", content=payload.content)

    # AI response
    reply_text = await process_query(chatbot, agent, payload.content, None, None)

    # Save assistant message
    ai_msg = await msg_service.create_message(db, conv_id, sender="assistant", content=reply_text)

    return MessageResponseDTO(
        msg_id=ai_msg.msg_id,
        conv_id=ai_msg.conv_id,
        sender=ai_msg.sender,
        content=ai_msg.content,
        created_at=ai_msg.created_at
    )


@router.get("/{conv_id}/history", response_model=List[MessageHistoryDTO])
async def conversation_history(
    conv_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all messages in a conversation"""
    history = await get_conversation_history(db, conv_id)
    return history
