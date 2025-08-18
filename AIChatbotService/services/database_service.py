from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from AIChatbotService.models import (
    Conversation,
    Message,
    Embedding
)
from AIChatbotService.database import db_manager
import uuid


class DatabaseService:
    # ---------------------------
    # Conversations
    # ---------------------------
    async def create_conversation(self, user_id: str, title: str = None, strategy: enumerate = None) -> Conversation:
        async with db_manager.get_session() as session:
            conversation = Conversation(
                user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
                title=title,
                strategy=strategy,  # wrap default in list
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation


    async def get_conversation(self, conv_id: str) -> Optional[Conversation]:
        async with db_manager.get_session() as session:
            stmt = (
                select(Conversation)
                .options(
                    selectinload(Conversation.messages)
                )
                .where(Conversation.conv_id == uuid.UUID(conv_id))
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        async with db_manager.get_session() as session:
            stmt = (
                select(Conversation)
                .where(Conversation.user_id == uuid.UUID(user_id))
                .order_by(Conversation.created_at.desc())
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def update_conversation(self, conv_id: str, title: str = None, strategy: str = None) -> bool:
        async with db_manager.get_session() as session:
            update_values = {}
            if title is not None:
                update_values["title"] = title
            if strategy is not None:
                update_values["strategy"] = strategy

            if not update_values:
                return False  

            stmt = (
                update(Conversation)
                .where(Conversation.conv_id == uuid.UUID(conv_id))
                .values(**update_values)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def delete_conversation(self, conv_id: str) -> bool:
        async with db_manager.get_session() as session:
            stmt = delete(Conversation).where(Conversation.conv_id == uuid.UUID(conv_id))
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    # ---------------------------
    # Messages
    # ---------------------------
    async def add_message(self, conv_id: str, sender: str, content: str) -> Message:
        async with db_manager.get_session() as session:
            message = Message(conv_id=uuid.UUID(conv_id), sender=sender, content=content)
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    async def get_message(self, msg_id: str) -> Optional[Message]:
        async with db_manager.get_session() as session:
            stmt = select(Message).where(Message.msg_id == uuid.UUID(msg_id))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_conversation_messages(self, conv_id: str) -> List[Message]:
        async with db_manager.get_session() as session:
            stmt = (
                select(Message)
                .where(Message.conv_id == uuid.UUID(conv_id))
                .order_by(Message.created_at.asc())
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def delete_message(self, msg_id: str) -> bool:
        async with db_manager.get_session() as session:
            stmt = delete(Message).where(Message.msg_id == uuid.UUID(msg_id))
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    # ---------------------------
    # Embeddings
    # ---------------------------
    async def create_embedding(self, content: str, embedding: list, meta_data: dict = None) -> Embedding:
        async with db_manager.get_session() as session:
            emb = Embedding(content=content, embedding=embedding, meta_data=meta_data or {})
            session.add(emb)
            await session.commit()
            await session.refresh(emb)
            return emb

    async def get_embedding(self, emb_id: str) -> Optional[Embedding]:
        async with db_manager.get_session() as session:
            stmt = select(Embedding).where(Embedding.id == uuid.UUID(emb_id))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def delete_embedding(self, emb_id: str) -> bool:
        async with db_manager.get_session() as session:
            stmt = delete(Embedding).where(Embedding.id == uuid.UUID(emb_id))
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
