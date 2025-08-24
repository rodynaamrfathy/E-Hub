from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import logging

from database import get_db_session
from services.images_service import ImageService
from services.images_classification_service import ImageClassificationService
from dto.ImageDTO import ImageDetailDTO, ImageHistoryDTO
from dto.ImageClassificationDTO import ImageClassificationDTO
from models import Image

router = APIRouter(tags=["Images"])
logger = logging.getLogger(__name__)


@router.post("/images/{image_id}/classify", response_model=ImageClassificationDTO)
async def classify_image(
    image_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Classify uploaded image"""
    try:
        service = ImageService()
        image = await service.get_image(db, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        # Check if classification already exists
        existing_classification = await ImageClassificationService.get_classification_by_image(db, image_id)
        if existing_classification:
            return ImageClassificationDTO(
                label=existing_classification.label,
                recycle_instructions=existing_classification.recycle_instructions
            )

        # Create new classification
        classification = await ImageClassificationService.create_classification(
            db, image_id, "plastic", "Rinse and recycle properly"
        )

        return ImageClassificationDTO(
            label=classification.label,
            recycle_instructions=classification.recycle_instructions
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error classifying image {image_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Classification failed")


@router.get("/images/history", response_model=List[ImageHistoryDTO])
async def image_history(db: AsyncSession = Depends(get_db_session)):
    """List uploaded images with classification"""
    try:
        stmt = select(Image).options(selectinload(Image.classification))
        result = await db.execute(stmt)
        images = result.scalars().all()

        history = []
        for img in images:
            if img.classification:
                history.append(ImageHistoryDTO(
                    image_id=img.image_id,
                    msg_id=img.msg_id,
                    label=img.classification.label,
                    recycle_instructions=img.classification.recycle_instructions,
                    created_at=img.created_at
                ))
        return history
    
    except Exception as e:
        logger.error(f"Error fetching image history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch image history")


@router.get("/images/{image_id}", response_model=ImageDetailDTO)
async def get_image(
    image_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Fetch a single image + classification"""
    try:
        logger.info(f"Fetching image with ID: {image_id}")
        
        # Validate image_id format
        if not image_id or image_id == "null" or image_id == "undefined":
            raise HTTPException(status_code=400, detail="Invalid image ID provided")

        service = ImageService()
        
        # Get image with classification eagerly loaded
        stmt = (
            select(Image)
            .options(selectinload(Image.classification))
            .filter(Image.image_id == image_id)
        )
        result = await db.execute(stmt)
        image = result.scalar_one_or_none()
        
        if not image:
            logger.warning(f"Image not found: {image_id}")
            raise HTTPException(status_code=404, detail="Image not found")

        if not image.classification:
            logger.warning(f"Classification not found for image: {image_id}")
            raise HTTPException(status_code=404, detail="Image classification not found")

        logger.info(f"Successfully fetched image {image_id}")
        return ImageDetailDTO(
            image_base64=image.image_base64,
            label=image.classification.label,
            recycle_instructions=image.classification.recycle_instructions
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching image {image_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")


@router.delete("/images/{image_id}")
async def delete_image(
    image_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete uploaded image"""
    try:
        if not image_id or image_id == "null" or image_id == "undefined":
            raise HTTPException(status_code=400, detail="Invalid image ID provided")
            
        service = ImageService()
        success = await service.delete_image(db, image_id)
        if not success:
            raise HTTPException(status_code=404, detail="Image not found")
        return {"message": f"Image {image_id} deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image {image_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete image")