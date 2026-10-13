from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, safe_next_url
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

router = APIRouter(tags=["pages:auth"])
templates = Jinja2Templates(directory="templates")


def _auth_cookie(response: RedirectResponse, token: str) -> RedirectResponse:
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax",
    )
    return response


def _default_post_login_url(user: User) -> str:
    if user.is_admin:
        return "/admin/services"
    return "/reservations"


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    next: str | None = None,
    user: User | None = Depends(get_current_user),
):
    if user:
        return RedirectResponse(
            url=safe_next_url(next, _default_post_login_url(user)),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "user": user, "next": next or ""},
    )


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form(""),
    db: Session = Depends(get_db),
):
    try:
        token, user = AuthService(db).login(email=email, password=password)
    except HTTPException:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "user": None,
                "next": next,
                "error": "Identifiants invalides",
            },
            status_code=400,
        )
    target = safe_next_url(next, _default_post_login_url(user))
    response = RedirectResponse(
        url=target,
        status_code=status.HTTP_303_SEE_OTHER,
    )
    return _auth_cookie(response, token)


@router.get("/register", response_class=HTMLResponse)
def register_page(
    request: Request,
    user: User | None = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "user": user},
    )


@router.post("/register")
def register_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    confirm: str = Form(...),
    db: Session = Depends(get_db),
):
    if password != confirm:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "user": None,
                "error": "Les mots de passe ne correspondent pas",
            },
            status_code=400,
        )
    try:
        data = UserCreate(
            full_name=full_name,
            email=email,
            phone=phone,
            password=password,
        )
        token, user = AuthService(db).register(data)
    except (HTTPException, ValidationError) as exc:
        detail = getattr(exc, "detail", "Données invalides")
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "user": None, "error": detail},
            status_code=400,
        )
    response = RedirectResponse(
        url=_default_post_login_url(user),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    return _auth_cookie(response, token)


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response
