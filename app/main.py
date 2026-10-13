from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine

# IMPORTANT : importer les modèles AVANT create_all
from app import models  # noqa: F401

from app.api.v1.router import api_router
from app.web import auth_pages, public_pages, client_pages, admin_pages


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version="1.0.0")

    # CORS (utile plus tard si tu ajoutes une app mobile ou front séparé)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Fichiers statiques
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Routes HTML (Jinja2)
    app.include_router(public_pages.router)
    app.include_router(auth_pages.router)
    app.include_router(client_pages.router)
    app.include_router(admin_pages.router)

    # Routes JSON (API v1)
    app.include_router(api_router, prefix="/api/v1")

    # Créer les tables en dev (en prod : alembic upgrade head)
    Base.metadata.create_all(bind=engine)

    from app.seed import seed_dev_admin

    seed_dev_admin()

    return app


app = create_app()