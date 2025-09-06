from fastapi import Depends, HTTPException, UploadFile, File, Form, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
import base64
import logging

from services.db.postgres import get_db_session
from services.repositories.images_service import ImageService
from services.repositories.message_service import MessageService
from services.repositories.images_classification_service import ImageClassificationService
from services.dto.ImageDTO import ImageUploadResponseDTO
from services.conversation.multimodal_chatbot import GeminiMultimodalChatbot


router = APIRouter(tags=["upload"])
logger = logging.getLogger(__name__)


@router.post("/upload-image", response_model=dict)
async def upload_image_with_message(
    conv_id: str = Form(...),
    query: str = Form(default="What type of waste is this and how should I recycle it?"),
    image_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)
):
    """Upload image with message and get AI response"""
    try:
        # Read and encode image
        content = await image_file.read()
        mime_type = image_file.content_type
        image_base64 = base64.b64encode(content).decode()

        # Create user message first
        msg_service = MessageService()
        user_msg = await msg_service.create_message(db, conv_id, sender="user", content=query)

        # Create image tied to the message
        image_service = ImageService()
        image = await image_service.create_image(db, str(user_msg.msg_id), mime_type, image_base64)

        # Process image with AI and get classification
        # For now, we'll use a simple classification - you can enhance this with actual AI
        classification_service = ImageClassificationService()
        
        # Simple classification logic (you can replace this with actual AI classification)
        classification = await classification_service.create_classification(
            db, str(image.image_id), "plastic", "Rinse clean and place in recycling bin"
        )

        # Generate AI response using the query and classification
        chatbot = GeminiMultimodalChatbot()

        # Combine user query with classification info
        prompt = f"{query} The image shows {classification.label} waste."

        # Stream or get full response
        async for token in chatbot.stream_response(prompt):
            pass  # (you can ignore streaming here if you just want final reply)

        ai_response = chatbot.get_full_response()


        # Save AI response as assistant message
        ai_msg = await msg_service.create_message(db, conv_id, sender="assistant", content=ai_response)

        return {
            "user_message": {
                "msg_id": user_msg.msg_id,
                "content": user_msg.content,
                "created_at": user_msg.created_at
            },
            "image": {
                "image_id": image.image_id,
                "msg_id": image.msg_id,
                "mime_type": image.mime_type
            },
            "classification": {
                "label": classification.label,
                "recycle_instructions": classification.recycle_instructions
            },
            "ai_response": {
                "msg_id": ai_msg.msg_id,
                "content": ai_msg.content,
                "created_at": ai_msg.created_at
            },
            "reply": ai_msg.content
        }

    except Exception as e:
        await db.rollback()
        logger.exception("Upload failed")   # <-- logs full traceback
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/images/upload-only", response_model=ImageUploadResponseDTO)
async def upload_image_only(
    msg_id: str = Form(...),
    image_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)
):
    """Upload image tied to an existing message (original functionality)"""
    try:
        # Verify message exists first
        msg_service = MessageService()
        message = await msg_service.get_message(db, msg_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        content = await image_file.read()
        mime_type = image_file.content_type
        image_base64 = base64.b64encode(content).decode()

        service = ImageService()
        image = await service.create_image(db, msg_id, mime_type, image_base64)

        return ImageUploadResponseDTO(
            image_id=image.image_id,
            msg_id=image.msg_id,
            mime_type=image.mime_type
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")