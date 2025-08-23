from sqlalchemy.orm import Session
from models import Message

class MessageService:
    @staticmethod
    def create_message(db: Session, conv_id: str, sender: str, content: str):
        message = Message(conv_id=conv_id, sender=sender, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_message(db: Session, msg_id: str):
        return db.query(Message).filter(Message.msg_id == msg_id).first()

    @staticmethod
    def list_messages(db: Session, conv_id: str):
        return db.query(Message).filter(Message.conv_id == conv_id).all()

    @staticmethod
    def delete_message(db: Session, msg_id: str):
        message = db.query(Message).filter(Message.msg_id == msg_id).first()
        if message:
            db.delete(message)
            db.commit()
            return True
        return False
