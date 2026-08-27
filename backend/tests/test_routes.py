import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    return app.test_client()

def test_peticion_sin_body_devuelve_400(client):
    response = client.post("/contact")     # ejecutar
    assert response.status_code == 400     # comprobar
    
def test_body_valido_devuelve_200(client, monkeypatch):
    monkeypatch.setattr(
        "routes.send_email",
        lambda data, config: {"success": True, "error": None, "status_code": 201},
    )
    response = client.post("/contact", json={
        "name": "Mauro",
        "email": "mauro@test.com",
        "message": "Hola",
        "consent": True,
    })
    assert response.status_code == 200
    
def test_honeypot_con_campos_invalidos_devuelve_200(client):
    response = client.post("/contact", json={
        "website": "http://spam.com"
    })
    assert response.status_code == 200    
    
def test_validacion_fallida_devuelve_400(client):
    response = client.post("/contact", json={
        "name": "Mauro",
        "email": "mauro@test.com",
        "consent": False,
    })
    assert "consent" in response.get_json()["errors"]
    assert response.status_code == 400

    
def test_fallo_del_proveedor_devuelve_502(client, monkeypatch):
    monkeypatch.setattr(
        "routes.send_email",
        lambda data, config: {"success": False, "error": "401 Client Error", "status_code": 401},
    )
    response = client.post("/contact", json={
        "name": "Mauro",
        "email": "mauro@test.com",
        "message": "Hola",
        "consent": True,
    })
    assert response.status_code == 502
    assert "401" not in response.get_data(as_text=True)
    
def test_sexta_peticion_devuelve_429(client):
    for _ in range(5):
        client.post("/contact")
    response = client.post("/contact")
    assert response.status_code == 429