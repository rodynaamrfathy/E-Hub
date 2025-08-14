from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from AIChatbotService.models import Conversation, Message, Base
from AIChatbotService.database import db_manager
import uuid

class DatabaseService:
    
    async def create_conversation(self, user_id: str, session_id: str, title: str = None) -> Conversation:
        """Create a new conversation"""
        async with db_manager.get_session() as session:
            conversation = Conversation(
                user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
                session_id=session_id,
                title=title
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID with messages"""
        async with db_manager.get_session() as session:
            stmt = select(Conversation).options(
                selectinload(Conversation.messages)
            ).where(Conversation.conversation_id == uuid.UUID(conversation_id))
            
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        async with db_manager.get_session() as session:
            stmt = select(Conversation).where(
                Conversation.user_id == uuid.UUID(user_id)
            ).order_by(Conversation.updated_at.desc())
            
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def add_message(self, conversation_id: str, message_type: str, content: str, msg_metadata: dict = None) -> Message:
        """Add a message to a conversation"""
        async with db_manager.get_session() as session:
            message = Message(
                message_type=message_type,
                content=content,
                msg_metadata=msg_metadata or {}
            )
            message.conversation_id = uuid.UUID(conversation_id)
            
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message
    
    async def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        async with db_manager.get_session() as session:
            stmt = update(Conversation).where(
                Conversation.conversation_id == uuid.UUID(conversation_id)
            ).values(title=title)
            
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        async with db_manager.get_session() as session:
            stmt = delete(Conversation).where(
                Conversation.conversation_id == uuid.UUID(conversation_id)
            )
            
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
    
    async def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages for a conversation"""
        async with db_manager.get_session() as session:
            stmt = select(Message).where(
                Message.conversation_id == uuid.UUID(conversation_id)
            ).order_by(Message.created_at.asc())
            
            result = await session.execute(stmt)
            return result.scalars().all()

# Usage Example
async def example_usage():
    """Example of how to use the database service"""
    
    # Initialize database
    await db_manager.initialize()
    await db_manager.create_tables()
    
    service = DatabaseService()
    
    try:
        # Create a conversation
        user_id = str(uuid.uuid4())
        session_id = "session_123"
        conversation = await service.create_conversation(
            user_id=user_id,
            session_id=session_id,
            title="Test Conversation"
        )
        print(f"Created conversation: {conversation}")
        
        # Add messages
        user_message = await service.add_message(
            conversation_id=str(conversation.conversation_id),
            message_type="user",
            content="Hello, how are you?",
            msg_metadata={"timestamp": "2024-01-01T10:00:00Z"}
        )
        
        bot_message = await service.add_message(
            conversation_id=str(conversation.conversation_id),
            message_type="assistant",
            content="I'm doing well, thank you for asking!",
            msg_metadata={"model": "claude-3", "tokens": 50}
        )
        
        # Get conversation with messages
        full_conversation = await service.get_conversation(str(conversation.conversation_id))
        print(f"Full conversation: {full_conversation}")
        print(f"Messages: {full_conversation.messages}")
        
        # Get user conversations
        user_conversations = await service.get_user_conversations(user_id)
        print(f"User conversations: {user_conversations}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await db_manager.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())