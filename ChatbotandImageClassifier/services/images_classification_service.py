from sqlalchemy.orm import Session
from models import ImageClassification

class ImageClassificationService:
    @staticmethod
    def create_classification(db: Session, image_id: str, label: str, recycle_instructions: str, confidence: float = None):
        classification = ImageClassification(
            image_id=image_id,
            label=label,
            recycle_instructions=recycle_instructions,
            confidence=confidence
        )
        db.add(classification)
        db.commit()
        db.refresh(classification)
        return classification

    @staticmethod
    def get_classification(db: Session, classification_id: str):
        return db.query(ImageClassification).filter(ImageClassification.classification_id == classification_id).first()

    @staticmethod
    def get_classification_by_image(db: Session, image_id: str):
        return db.query(ImageClassification).filter(ImageClassification.image_id == image_id).first()

    @staticmethod
    def delete_classification(db: Session, classification_id: str):
        classification = db.query(ImageClassification).filter(ImageClassification.classification_id == classification_id).first()
        if classification:
            db.delete(classification)
            db.commit()
            return True
        return False
