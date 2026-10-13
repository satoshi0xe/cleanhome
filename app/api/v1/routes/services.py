from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.service import ServiceOut
from app.services.service_service import ServiceService

router = APIRouter(prefix="/services", tags=["api:services"])


@router.get("/", response_model=list[ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return ServiceService(db).list_all()


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    return ServiceService(db).get_by_id(service_id)
