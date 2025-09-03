from langchain.schema.messages import HumanMessage
from typing import List, Dict

class MessageBuilder:
    """Handles creation of different message types."""
    
    @staticmethod
    def create_multimodal_message(text: str, 
                                images: List[Dict[str, str]], 
                                default_mime: str = "image/jpeg") -> HumanMessage:
        """Create a multimodal message with text and images."""
        if not images:
            return HumanMessage(content=text)

        content = []
        if text:
            content.append({"type": "text", "text": text})

        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img.get('mime_type', default_mime)};base64,{img['data']}"
                }
            })

        return HumanMessage(content=content)

