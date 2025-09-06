from fastapi import Depends, HTTPException, UploadFile, File, APIRouter
from services.repositories.images_service import ImageService
from services.dto.ImageDTO import ImageUploadResponseDTO
import uuid
import logging
from services.db.postgres import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
import base64


router = APIRouter(tags=["upload_router"])
logger = logging.getLogger(__name__)


@router.post("/upload-image", response_model=ImageUploadResponseDTO)
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Upload an image file (similar to OpenAI's backend).
    Returns an ID or URL reference that can be used in conversation.
    """
    try:
        # Read file contents
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Generate unique ID for this image
        image_id = str(uuid.uuid4())

        # Convert to base64 for DB storage
        image_base64 = base64.b64encode(contents).decode("utf-8")

        # Save to DB
        await ImageService.create_image(
            db=db,
            msg_id=image_id,  # if msg_id is different, adjust here
            mime_type=file.content_type,
            image_base64=image_base64
        )

        # Return reference (like OpenAI returns file IDs)
        return ImageUploadResponseDTO(
            image_id=image_id,
            filename=file.filename,
            content_type=file.content_type,
            size=len(contents),
            url=f"/api/chat/images/{image_id}"
        )

    except Exception as e:
        logger.exception("Image upload failed")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
