from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models import Image
from uuid import UUID

class ImageService:
    @staticmethod
    async def create_image(db: AsyncSession, msg_id: str, mime_type: str, image_base64: str):
        image = Image(msg_id=UUID(msg_id), mime_type=mime_type, image_base64=image_base64)
        db.add(image)
        await db.commit()
        await db.refresh(image)
        return image

    @staticmethod
    async def get_image(db: AsyncSession, image_id: str):
        result = await db.execute(select(Image).filter(Image.image_id == image_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_images_by_message(db: AsyncSession, msg_id: str):
        result = await db.execute(select(Image).filter(Image.msg_id == msg_id))
        return result.scalars().all()

    @staticmethod
    async def delete_image(db: AsyncSession, image_id: str):
        result = await db.execute(delete(Image).filter(Image.image_id == image_id))
        await db.commit()
        return result.rowcount > 0