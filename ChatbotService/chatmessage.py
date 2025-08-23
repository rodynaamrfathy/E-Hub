import uuid
from datetime import datetime

class ChatMessage:
    """Represents a chat message with text and optional images"""
    def __init__(self, role, content=None, images=None):
        self.id = str(uuid.uuid4())
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.images = images or []
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'images': self.images,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        msg = cls(data['role'], data['content'], data.get('images', []))
        msg.id = data.get('id', str(uuid.uuid4()))
        msg.timestamp = data.get('timestamp', datetime.now().isoformat())
        return msg
