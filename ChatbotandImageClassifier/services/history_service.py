from sqlalchemy.orm import Session, joinedload
from models import Message
from typing import List

def get_conversation_history(db: Session, conv_id: str) -> List[dict]:
    """
    Fetch all messages for a given conversation, ordered by created_at.
    Includes text messages and any attached images with classification.
    """
    messages = (
        db.query(Message)
        .filter(Message.conv_id == conv_id)
        .options(joinedload(Message.images).joinedload("classification"))
        .order_by(Message.created_at.asc())
        .all()
    )

    history = []
    for msg in messages:
        entry = {
            "role": msg.sender,  # "user" or "assistant"
            "timestamp": msg.created_at,
            "type": "text" if not msg.images else "image",
            "content": msg.content
        }

        # Attach images if any
        if msg.images:
            entry["images"] = []
            for img in msg.images:
                img_entry = {
                    "image_id": img.image_id,
                    "mime_type": img.mime_type,
                    "image_base64": img.image_base64
                }
                if img.classification:
                    img_entry.update({
                        "label": img.classification.label,
                        "recycle_instructions": img.classification.recycle_instructions
                    })
                entry["images"].append(img_entry)

        history.append(entry)

    return history
