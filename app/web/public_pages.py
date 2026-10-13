from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.service_service import ServiceService

router = APIRouter(tags=["pages:public"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def catalogue(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    services = ServiceService(db).list_all()
    return templates.TemplateResponse(
        "public/index.html",
        {"request": request, "services": services, "user": user},
    )


@router.get("/service/{service_id}", response_class=HTMLResponse)
def service_detail(
    service_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    service = ServiceService(db).get_by_id(service_id)
    return templates.TemplateResponse(
        "public/service_detail.html",
        {"request": request, "service": service, "user": user},
    )
