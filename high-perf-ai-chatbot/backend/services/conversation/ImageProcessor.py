import io, base64
from typing import Dict, List, Optional, Union
from PIL import Image


class ImageProcessor:
    """Handles image processing and preparation."""
    
    @staticmethod
    def prepare_image(image: Union[str, bytes, io.IOBase, Dict], 
                     max_size: tuple = (256, 256)) -> Optional[Dict[str, str]]:
        """
        Prepares image input into a dict with base64 data and optional mime_type.
        
        Args:
            image: Image input (dict, path, bytes, or file-like object)
            max_size: Maximum size for image resizing
            
        Returns:
            Dict with 'data' and optional 'mime_type' keys, or None if processing fails
        """
        try:
            # If already provided as base64 dict from client, pass through
            if isinstance(image, dict) and image.get("data"):
                data = image.get("data")
                mime = image.get("mime_type")
                return {"data": data, **({"mime_type": mime} if mime else {})}

            # Otherwise, treat as file path or file-like
            with Image.open(image) as img:
                img.thumbnail(max_size)
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                encoded = base64.b64encode(buffer.getvalue()).decode()
            return {"data": encoded, "mime_type": "image/png"}
            
        except Exception as e:
            print(f"Error processing image {image}: {e}")
            return None

    @staticmethod
    def process_images(images: Optional[List]) -> List[Dict[str, str]]:
        """Process multiple images and return list of prepared image dicts."""
        if not images:
            return []
        
        processed = []
        for img in images:
            if img:
                prepared = ImageProcessor.prepare_image(img)
                if prepared:
                    processed.append(prepared)
        return processed

