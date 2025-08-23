from sqlalchemy.orm import Session
from models import Message

def get_conversation_history(db: Session, conversation_id: int):
    """
    Fetch all messages for a given conversation, ordered by created_at.
    Includes both text and image messages.
    Separates User and AI clearly.
    """
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    history = []
    for msg in messages:
        entry = {
            "role": "user" if msg.sender_type == "user" else "ai",
            "timestamp": msg.created_at,
            "type": msg.message_type,  # "text" or "image"
        }

        if msg.message_type == "text":
            entry["content"] = msg.content
        elif msg.message_type == "image":
            entry["image_url"] = msg.image_url
            if msg.content:  # optional description
                entry["description"] = msg.content

        history.append(entry)

    return history