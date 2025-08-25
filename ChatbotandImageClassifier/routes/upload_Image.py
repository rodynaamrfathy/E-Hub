from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import base64
from uuid import UUID

from database import get_db_session
from services.images_service import ImageService
from services.message_service import MessageService
from services.images_classification_service import ImageClassificationService
from dto.ImageDTO import ImageUploadResponseDTO
from dto.MessageDTO import MessageResponseDTO
# from utils.botutils import process_query
# from core.initializers import chatbot, agent

router = APIRouter(tags=["Upload"])


@router.post("/images/upload", response_model=dict)
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
        ai_response = await process_query(
            chatbot, 
            agent, 
            f"{query} The image shows {classification.label} waste.", 
            None, 
            None
        )

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
            }
        }

    except Exception as e:
        await db.rollback()
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