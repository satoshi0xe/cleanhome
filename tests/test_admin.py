from fastapi.testclient import TestClient

from app.models.service import Service
from app.models.user import User
from tests.conftest import login, tomorrow


def test_client_ne_peut_pas_acceder_admin(
    client: TestClient,
    client_user: User,
) -> None:
    login(client, client_user.email, "secret12")
    response = client.get("/admin/services", follow_redirects=False)
    assert response.status_code == 403


def test_admin_ajoute_une_prestation(
    client: TestClient,
    admin_user: User,
) -> None:
    login(client, admin_user.email, "admin123")
    response = client.post(
        "/admin/services/new",
        data={
            "name": "Nettoyage vitres",
            "category": "Vitres",
            "description": "Vitres intérieures et extérieures.",
            "price": "8000",
            "duration": "2 heures",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/services"

    listing = client.get("/admin/services")
    assert listing.status_code == 200
    assert "Nettoyage vitres" in listing.text


def test_admin_modifie_une_prestation(
    client: TestClient,
    admin_user: User,
    service: Service,
) -> None:
    login(client, admin_user.email, "admin123")
    page = client.get(f"/admin/services/{service.id}/edit")
    assert page.status_code == 200
    assert service.name in page.text

    response = client.post(
        f"/admin/services/{service.id}/edit",
        data={
            "name": "Grand ménage 3 pièces",
            "category": "Grand ménage",
            "description": "Nettoyage en profondeur.",
            "price": "25000",
            "duration": "5 heures",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/services"

    listing = client.get("/admin/services")
    assert "Grand ménage 3 pièces" in listing.text
    assert "25 000 FCFA" in listing.text or "25000" in listing.text

    public = client.get(f"/service/{service.id}")
    assert public.status_code == 200
    assert "Grand ménage 3 pièces" in public.text


def test_admin_change_statut_reservation(
    client: TestClient,
    admin_user: User,
    client_user: User,
    service: Service,
) -> None:
    login(client, client_user.email, "secret12")
    booked = client.post(
        f"/book/{service.id}",
        data={
            "date": tomorrow(),
            "address": "Cocody Riviera 3",
            "phone": client_user.phone,
        },
        follow_redirects=False,
    )
    assert booked.status_code == 303

    client.cookies.clear()
    login(client, admin_user.email, "admin123")
    updated = client.post(
        "/admin/bookings/1/status",
        data={"status": "confirmed"},
        follow_redirects=False,
    )
    assert updated.status_code == 303

    page = client.get("/admin/reservations")
    assert page.status_code == 200
    assert 'value="confirmed"' in page.text
    assert "selected" in page.text
