from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models import Message
from uuid import UUID

class MessageService:
    @staticmethod
    async def create_message(db: AsyncSession, conv_id: str, sender: str, content: str):
        message = Message(conv_id=UUID(conv_id), sender=sender, content=content)
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_message(db: AsyncSession, msg_id: str):
        result = await db.execute(select(Message).filter(Message.msg_id == msg_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_messages(db: AsyncSession, conv_id: str):
        result = await db.execute(select(Message).filter(Message.conv_id == conv_id))
        return result.scalars().all()

    @staticmethod
    async def delete_message(db: AsyncSession, msg_id: str):
        result = await db.execute(delete(Message).filter(Message.msg_id == msg_id))
        await db.commit()
        return result.rowcount > 0