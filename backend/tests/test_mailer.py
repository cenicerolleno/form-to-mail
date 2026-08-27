from unittest.mock import MagicMock
from services.mailer import send_email
import requests

class FakeConfig:
    MAIL_FROM = "remitente@test.com"
    MAIL_TO = "destino@test.com"
    BREVO_API_KEY = "clave-falsa"
    
fake_data = {
    "name": "Mauro",
    "email": "mauro@test.com",
    "phone": "123456789",
    "message": "Hola, este es un mensaje de prueba.",
}


def test_envio_exitoso(monkeypatch):
    fake_post = MagicMock()
    fake_post.return_value.status_code = 200
    fake_post.return_value.raise_for_status.return_value = None
    monkeypatch.setattr("services.mailer.requests.post", fake_post)

    
    result = send_email(fake_data, FakeConfig)
    assert result["success"] is True
    assert result["error"] is None
    assert result["status_code"] == 200
    
def test_envio_fallido(monkeypatch):
    fake_response = MagicMock()
    fake_response.status_code = 401

    fake_post = MagicMock()
    fake_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error", response=fake_response)
    monkeypatch.setattr("services.mailer.requests.post", fake_post)
    
    result = send_email(fake_data, FakeConfig)
    assert result["success"] is False
    assert "401 Client Error" in result["error"] 
    assert result["status_code"] == 401
    
def test_error_de_conexion(monkeypatch):
    fake_post = MagicMock()
    fake_post.side_effect = requests.exceptions.ConnectionError("Error de conexión")
    monkeypatch.setattr("services.mailer.requests.post", fake_post)

    
    result = send_email(fake_data, FakeConfig)
    assert result["success"] is False
    assert "Error de conexión" in result["error"]
    assert result["status_code"] is None
    
def test_payload_correcto(monkeypatch):
    fake_post = MagicMock()
    monkeypatch.setattr("services.mailer.requests.post", fake_post)

    
    send_email(fake_data, FakeConfig)
    
    args, kwargs = fake_post.call_args
    payload = kwargs["json"]
    
    assert payload["sender"]["email"] == FakeConfig.MAIL_FROM
    assert payload["to"][0]["email"] == FakeConfig.MAIL_TO
    assert payload["replyTo"]["email"] == fake_data["email"]
    assert payload["subject"] == "Nuevo mensaje desde el formulario web"
    assert "Nuevo contacto desde el formulario web" in payload["textContent"]