from sqlalchemy.orm import Session
from models import Conversation

class ConversationService:
    @staticmethod
    def create_conversation(db: Session, user_id: str, title: str = None):
        conversation = Conversation(user_id=user_id, title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(db: Session, conv_id: str):
        return db.query(Conversation).filter(Conversation.conv_id == conv_id).first()

    @staticmethod
    def list_conversations(db: Session, user_id: str):
        return db.query(Conversation).filter(Conversation.user_id == user_id).all()

    @staticmethod
    def delete_conversation(db: Session, conv_id: str):
        conversation = db.query(Conversation).filter(Conversation.conv_id == conv_id).first()
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False
