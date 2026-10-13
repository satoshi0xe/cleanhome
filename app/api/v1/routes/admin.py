from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.booking import BookingOut, BookingStatusUpdate
from app.schemas.service import ServiceCreate, ServiceOut, ServiceUpdate
from app.services.booking_service import BookingService
from app.services.service_service import ServiceService

router = APIRouter(prefix="/admin", tags=["api:admin"])


@router.get("/bookings", response_model=list[BookingOut])
def admin_list_bookings(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return BookingService(db).list_all()


@router.patch("/bookings/{booking_id}/status", response_model=BookingOut)
def admin_update_booking_status(
    booking_id: int,
    data: BookingStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return BookingService(db).update_status(booking_id, data.status)


@router.post("/services", response_model=ServiceOut, status_code=201)
def admin_create_service(
    data: ServiceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return ServiceService(db).create(data)


@router.put("/services/{service_id}", response_model=ServiceOut)
def admin_update_service(
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return ServiceService(db).update(service_id, data)


@router.delete("/services/{service_id}", status_code=204)
def admin_delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    ServiceService(db).delete(service_id)
    return None
