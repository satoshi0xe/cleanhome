import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.service import Service
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceUpdate

UPLOAD_DIR = Path("static/img/services")


class ServiceService:
    """Logique métier des prestations de ménage."""

    def __init__(self, db: Session):
        self.repo = ServiceRepository(db)

    def list_all(self) -> list[Service]:
        return self.repo.list_all()

    def get_by_id(self, service_id: int) -> Service:
        service = self.repo.get_by_id(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prestation introuvable",
            )
        return service

    def create(self, data: ServiceCreate) -> Service:
        return self.repo.create(
            name=data.name,
            category=data.category,
            description=data.description,
            price=data.price,
            duration=data.duration,
            image_url=data.image_url,
        )

    def update(self, service_id: int, data: ServiceUpdate) -> Service:
        service = self.get_by_id(service_id)
        image_url = data.image_url if data.image_url else service.image_url
        return self.repo.update(
            service,
            name=data.name,
            category=data.category,
            description=data.description,
            price=data.price,
            duration=data.duration,
            image_url=image_url,
        )

    def delete(self, service_id: int) -> None:
        service = self.get_by_id(service_id)
        try:
            self.repo.delete(service)
        except IntegrityError as exc:
            self.repo.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de supprimer : des réservations y sont liées",
            ) from exc

    @staticmethod
    def save_image(image: UploadFile) -> str | None:
        """Enregistre une image uploadée et renvoie l'URL publique."""
        if not image.filename:
            return None

        suffix = Path(image.filename).suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format d'image non supporté (PNG ou JPG)",
            )

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4().hex}{suffix}"
        destination = UPLOAD_DIR / filename
        destination.write_bytes(image.file.read())
        return f"/static/img/services/{filename}"
