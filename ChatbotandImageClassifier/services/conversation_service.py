from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models import Conversation
from uuid import UUID

class ConversationService:
    @staticmethod
    async def create_conversation(db: AsyncSession, user_id: str, title: str = None):
        conversation = Conversation(user_id=UUID(user_id) if user_id != "default" else None, title=title)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def get_conversation(db: AsyncSession, conv_id: str):
        result = await db.execute(select(Conversation).filter(Conversation.conv_id == conv_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_conversations(db: AsyncSession, user_id: str):
        # For now, get all conversations since user_id is "default"
        result = await db.execute(select(Conversation).order_by(Conversation.updated_at.desc()))
        return result.scalars().all()

    @staticmethod
    async def delete_conversation(db: AsyncSession, conv_id: str):
        result = await db.execute(delete(Conversation).filter(Conversation.conv_id == conv_id))
        await db.commit()
        return result.rowcount > 0