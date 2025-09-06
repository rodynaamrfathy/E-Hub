from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models import ImageClassification
from uuid import UUID

class ImageClassificationService:
    @staticmethod
    async def create_classification(db: AsyncSession, image_id: str, label: str, recycle_instructions: str):
        classification = ImageClassification(
            image_id=UUID(image_id),
            label=label,
            recycle_instructions=recycle_instructions
        )
        db.add(classification)
        await db.commit()
        await db.refresh(classification)
        return classification

    @staticmethod
    async def get_classification(db: AsyncSession, classification_id: str):
        result = await db.execute(select(ImageClassification).filter(ImageClassification.classification_id == classification_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_classification_by_image(db: AsyncSession, image_id: str):
        result = await db.execute(select(ImageClassification).filter(ImageClassification.image_id == image_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_classification(db: AsyncSession, classification_id: str):
        result = await db.execute(delete(ImageClassification).filter(ImageClassification.classification_id == classification_id))
        await db.commit()
        return result.rowcount > 0