from fastapi.testclient import TestClient

from app.models.service import Service


def test_catalogue_affiche_les_prestations(
    client: TestClient,
    service: Service,
) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert service.name in response.text


def test_detail_prestation(client: TestClient, service: Service) -> None:
    response = client.get(f"/service/{service.id}")
    assert response.status_code == 200
    assert "FCFA" in response.text
    assert service.name in response.text


def test_detail_inconnu_renvoie_404(client: TestClient) -> None:
    response = client.get("/service/999")
    assert response.status_code == 404


def test_api_liste_services(client: TestClient, service: Service) -> None:
    response = client.get("/api/v1/services/")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == service.id
    assert payload[0]["price"] == 15000
