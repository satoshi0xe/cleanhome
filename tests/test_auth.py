from fastapi.testclient import TestClient

from app.models.service import Service
from app.models.user import User
from tests.conftest import login


def test_register_puis_acces_reservations(client: TestClient) -> None:
    response = client.post(
        "/register",
        data={
            "full_name": "Kofi Yao",
            "email": "kofi@test.ci",
            "phone": "0700223344",
            "password": "secret12",
            "confirm": "secret12",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/reservations"

    page = client.get("/reservations")
    assert page.status_code == 200
    assert "Mes réservations" in page.text


def test_register_mots_de_passe_differents(client: TestClient) -> None:
    response = client.post(
        "/register",
        data={
            "full_name": "Kofi Yao",
            "email": "kofi@test.ci",
            "phone": "0700223344",
            "password": "secret12",
            "confirm": "autre",
        },
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "ne correspondent pas" in response.text


def test_login_admin_redirige_vers_admin(
    client: TestClient,
    admin_user: User,
) -> None:
    response = client.post(
        "/login",
        data={"email": admin_user.email, "password": "admin123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/services"


def test_page_protegee_redirige_vers_login(
    client: TestClient,
    service: Service,
) -> None:
    response = client.get(f"/book/{service.id}", follow_redirects=False)
    assert response.status_code == 303
    assert "/login?next=" in response.headers["location"]


def test_login_puis_retour_sur_next(
    client: TestClient,
    client_user: User,
    service: Service,
) -> None:
    response = client.post(
        "/login",
        data={
            "email": client_user.email,
            "password": "secret12",
            "next": f"/book/{service.id}",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == f"/book/{service.id}"


def test_open_redirect_refuse(
    client: TestClient,
    client_user: User,
) -> None:
    response = client.post(
        "/login",
        data={
            "email": client_user.email,
            "password": "secret12",
            "next": "https://evil.example",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/reservations"


def test_logout_efface_la_session(
    client: TestClient,
    client_user: User,
) -> None:
    login(client, client_user.email, "secret12")
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 303
    guarded = client.get("/reservations", follow_redirects=False)
    assert guarded.status_code == 303


def test_api_login(client: TestClient, client_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": client_user.email, "password": "secret12"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
