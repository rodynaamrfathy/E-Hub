from sqlalchemy.orm import Session
from models import Image

class ImageService:
    @staticmethod
    def create_image(db: Session, msg_id: str, mime_type: str, image_base64: str):
        image = Image(msg_id=msg_id, mime_type=mime_type, image_base64=image_base64)
        db.add(image)
        db.commit()
        db.refresh(image)
        return image

    @staticmethod
    def get_image(db: Session, image_id: str):
        return db.query(Image).filter(Image.image_id == image_id).first()

    @staticmethod
    def list_images_by_message(db: Session, msg_id: str):
        return db.query(Image).filter(Image.msg_id == msg_id).all()

    @staticmethod
    def delete_image(db: Session, image_id: str):
        image = db.query(Image).filter(Image.image_id == image_id).first()
        if image:
            db.delete(image)
            db.commit()
            return True
        return False
