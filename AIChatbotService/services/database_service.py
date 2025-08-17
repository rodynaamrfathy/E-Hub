from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from AIChatbotService.models import (
    Conversation,
    Message,
    Embedding,
    Strategy,
    ConversationStrategy,
)
from AIChatbotService.database import db_manager
import uuid


class DatabaseService:
    # ---------------------------
    # Conversations
    # ---------------------------
    async def create_conversation(self, user_id: str, title: str = None) -> Conversation:
        async with db_manager.get_session() as session:
            conversation = Conversation(
                user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
                title=title,
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
                    selectinload(Conversation.messages),
                    selectinload(Conversation.strategies).selectinload(ConversationStrategy.strategy),
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

    async def update_conversation_title(self, conv_id: str, title: str) -> bool:
        async with db_manager.get_session() as session:
            stmt = (
                update(Conversation)
                .where(Conversation.conv_id == uuid.UUID(conv_id))
                .values(title=title)
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

    # ---------------------------
    # Strategies
    # ---------------------------
    async def create_strategy(self, name: str, description: str) -> Strategy:
        async with db_manager.get_session() as session:
            strategy = Strategy(name=name, description=description)
            session.add(strategy)
            await session.commit()
            await session.refresh(strategy)
            return strategy

    async def get_strategy(self, strategy_id: int) -> Optional[Strategy]:
        async with db_manager.get_session() as session:
            stmt = select(Strategy).where(Strategy.strategy_id == strategy_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_strategies(self) -> List[Strategy]:
        async with db_manager.get_session() as session:
            stmt = select(Strategy)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def delete_strategy(self, strategy_id: int) -> bool:
        async with db_manager.get_session() as session:
            stmt = delete(Strategy).where(Strategy.strategy_id == strategy_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    # ---------------------------
    # Conversation <-> Strategies
    # ---------------------------
    async def add_strategy_to_conversation(self, conv_id: str, strategy_id: int) -> ConversationStrategy:
        async with db_manager.get_session() as session:
            conv_strategy = ConversationStrategy(
                conv_id=uuid.UUID(conv_id), strategy_id=strategy_id
            )
            session.add(conv_strategy)
            await session.commit()
            await session.refresh(conv_strategy)
            return conv_strategy

    async def get_conversation_strategies(self, conv_id: str) -> List[Strategy]:
        async with db_manager.get_session() as session:
            stmt = (
                select(Strategy)
                .join(ConversationStrategy, Strategy.strategy_id == ConversationStrategy.strategy_id)
                .where(ConversationStrategy.conv_id == uuid.UUID(conv_id))
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def remove_strategy_from_conversation(self, conv_id: str, strategy_id: int) -> bool:
        async with db_manager.get_session() as session:
            stmt = delete(ConversationStrategy).where(
                ConversationStrategy.conv_id == uuid.UUID(conv_id),
                ConversationStrategy.strategy_id == strategy_id,
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
