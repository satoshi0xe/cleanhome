from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin_page
from app.models.user import User
from app.schemas.booking import BookingStatus
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.booking_service import BookingService
from app.services.service_service import ServiceService

router = APIRouter(tags=["pages:admin"])
templates = Jinja2Templates(directory="templates")


@router.get("/admin/services", response_class=HTMLResponse)
def admin_services(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_page),
):
    services = ServiceService(db).list_all()
    return templates.TemplateResponse(
        "admin/services.html",
        {"request": request, "services": services, "user": user},
    )


@router.get("/admin/services/new", response_class=HTMLResponse)
def admin_service_new_page(
    request: Request,
    user: User = Depends(require_admin_page),
):
    return templates.TemplateResponse(
        "admin/service_new.html",
        {"request": request, "user": user},
    )


@router.post("/admin/services/new")
def admin_service_new_submit(
    request: Request,
    name: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    duration: str = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_page),
):
    try:
        image_url = ServiceService.save_image(image) if image else None
        data = ServiceCreate(
            name=name,
            category=category,
            description=description,
            price=price,
            duration=duration,
            image_url=image_url,
        )
        ServiceService(db).create(data)
    except (HTTPException, ValidationError) as exc:
        detail = getattr(exc, "detail", "Données invalides")
        return templates.TemplateResponse(
            "admin/service_new.html",
            {"request": request, "user": user, "error": detail},
            status_code=400,
        )
    return RedirectResponse(
        url="/admin/services",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/admin/services/{service_id}/edit", response_class=HTMLResponse)
def admin_service_edit_page(
    service_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_page),
):
    service = ServiceService(db).get_by_id(service_id)
    return templates.TemplateResponse(
        "admin/service_edit.html",
        {"request": request, "user": user, "service": service},
    )


@router.post("/admin/services/{service_id}/edit")
def admin_service_edit_submit(
    service_id: int,
    request: Request,
    name: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    duration: str = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_page),
):
    service = ServiceService(db).get_by_id(service_id)
    try:
        image_url = ServiceService.save_image(image) if image else None
        data = ServiceUpdate(
            name=name,
            category=category,
            description=description,
            price=price,
            duration=duration,
            image_url=image_url,
        )
        ServiceService(db).update(service_id, data)
    except (HTTPException, ValidationError) as exc:
        detail = getattr(exc, "detail", "Données invalides")
        return templates.TemplateResponse(
            "admin/service_edit.html",
            {
                "request": request,
                "user": user,
                "service": service,
                "error": detail,
            },
            status_code=400,
        )
    return RedirectResponse(
        url="/admin/services",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/admin/services/{service_id}/delete")
def admin_service_delete(
    service_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_page),
):
    ServiceService(db).delete(service_id)
    return RedirectResponse(
        url="/admin/services",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/admin/reservations", response_class=HTMLResponse)
def admin_reservations(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_page),
):
    bookings = BookingService(db).list_all()
    return templates.TemplateResponse(
        "admin/reservations.html",
        {"request": request, "bookings": bookings, "user": user},
    )


@router.post("/admin/bookings/{booking_id}/status")
def admin_booking_status(
    booking_id: int,
    status_value: BookingStatus = Form(..., alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_page),
):
    BookingService(db).update_status(booking_id, status_value)
    return RedirectResponse(
        url="/admin/reservations",
        status_code=status.HTTP_303_SEE_OTHER,
    )
