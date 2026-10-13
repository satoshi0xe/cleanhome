from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.models.service import Service
from app.models.user import User
from tests.conftest import login, tomorrow


def test_reservation_complete(
    client: TestClient,
    client_user: User,
    service: Service,
) -> None:
    login(client, client_user.email, "secret12")
    response = client.post(
        f"/book/{service.id}",
        data={
            "date": tomorrow(),
            "address": "Cocody Riviera 3",
            "phone": client_user.phone,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"].startswith("/confirmation/")

    confirm = client.get(response.headers["location"])
    assert confirm.status_code == 200
    assert "Réservation confirmée" in confirm.text
    assert "En attente" in confirm.text

    listing = client.get("/reservations")
    assert listing.status_code == 200
    assert service.name in listing.text
    assert "Cocody Riviera 3" in listing.text


def test_date_passee_refusee(
    client: TestClient,
    client_user: User,
    service: Service,
) -> None:
    login(client, client_user.email, "secret12")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    response = client.post(
        f"/book/{service.id}",
        data={
            "date": yesterday,
            "address": "Cocody",
            "phone": client_user.phone,
        },
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "aujourd" in response.text
