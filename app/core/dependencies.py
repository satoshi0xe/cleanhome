from urllib.parse import quote, urlparse

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Récupère l'utilisateur depuis le cookie 'access_token' (posé au login HTML)."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.get(User, int(user_id))


def require_user(user: User | None = Depends(get_current_user)) -> User:
    """Pour l'API JSON : 401 si non connecté."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    return user


def require_admin(user: User | None = Depends(get_current_user)) -> User:
    """Pour l'API JSON : 403 si non admin."""
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur requis",
        )
    return user


def _login_redirect(request: Request) -> HTTPException:
    next_path = request.url.path
    if request.url.query:
        next_path = f"{next_path}?{request.url.query}"
    location = f"/login?next={quote(next_path, safe='')}"
    return HTTPException(
        status_code=status.HTTP_303_SEE_OTHER,
        detail="Non authentifié",
        headers={"Location": location},
    )


def require_user_page(
    request: Request,
    user: User | None = Depends(get_current_user),
) -> User:
    """Pour les pages HTML : redirige vers /login si non connecté."""
    if not user:
        raise _login_redirect(request)
    return user


def require_admin_page(
    request: Request,
    user: User | None = Depends(get_current_user),
) -> User:
    """Pour les pages HTML admin : login puis 403 si non admin."""
    if not user:
        raise _login_redirect(request)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur requis",
        )
    return user


def safe_next_url(raw: str | None, fallback: str) -> str:
    """N'accepte que des chemins relatifs locaux (anti open-redirect)."""
    if not raw:
        return fallback
    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        return fallback
    if not raw.startswith("/"):
        return fallback
    return raw
