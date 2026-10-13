from sqlalchemy.orm import Session

from app.models.service import Service


class ServiceRepository:
    """Accès BDD pour les prestations de ménage."""

    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Service]:
        return self.db.query(Service).order_by(Service.created_at.desc()).all()

    def get_by_id(self, service_id: int) -> Service | None:
        return self.db.get(Service, service_id)

    def create(
        self,
        *,
        name: str,
        category: str,
        description: str,
        price: int,
        duration: str,
        image_url: str | None = None,
    ) -> Service:
        service = Service(
            name=name,
            category=category,
            description=description,
            price=price,
            duration=duration,
            image_url=image_url,
        )
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service

    def update(
        self,
        service: Service,
        *,
        name: str,
        category: str,
        description: str,
        price: int,
        duration: str,
        image_url: str | None,
    ) -> Service:
        service.name = name
        service.category = category
        service.description = description
        service.price = price
        service.duration = duration
        service.image_url = image_url
        self.db.commit()
        self.db.refresh(service)
        return service

    def delete(self, service: Service) -> None:
        self.db.delete(service)
        self.db.commit()
