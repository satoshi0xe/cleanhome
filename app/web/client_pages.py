from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_user_page
from app.models.user import User
from app.services.booking_service import BookingService
from app.services.service_service import ServiceService

router = APIRouter(tags=["pages:client"])
templates = Jinja2Templates(directory="templates")


@router.get("/book/{service_id}", response_class=HTMLResponse)
def book_page(
    service_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user_page),
):
    service = ServiceService(db).get_by_id(service_id)
    return templates.TemplateResponse(
        "client/book.html",
        {"request": request, "service": service, "user": user},
    )


@router.post("/book/{service_id}")
def book_submit(
    service_id: int,
    request: Request,
    address: str = Form(...),
    phone: str = Form(...),
    booking_date: date = Form(..., alias="date"),
    db: Session = Depends(get_db),
    user: User = Depends(require_user_page),
):
    service = ServiceService(db).get_by_id(service_id)
    try:
        booking = BookingService(db).create(
            user=user,
            service_id=service_id,
            booking_date=booking_date,
            address=address,
            phone=phone,
        )
    except HTTPException as exc:
        return templates.TemplateResponse(
            "client/book.html",
            {
                "request": request,
                "service": service,
                "user": user,
                "error": exc.detail,
            },
            status_code=400,
        )
    return RedirectResponse(
        url=f"/confirmation/{booking.id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/confirmation/{booking_id}", response_class=HTMLResponse)
def confirmation(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user_page),
):
    booking = BookingService(db).get_for_user(booking_id, user)
    return templates.TemplateResponse(
        "client/confirmation.html",
        {"request": request, "booking": booking, "user": user},
    )


@router.get("/reservations", response_class=HTMLResponse)
def reservations(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user_page),
):
    bookings = BookingService(db).list_for_user(user.id)
    return templates.TemplateResponse(
        "client/reservations.html",
        {"request": request, "bookings": bookings, "user": user},
    )
