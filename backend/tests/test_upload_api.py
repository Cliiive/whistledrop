# backend/tests/test_upload_api.py
import pytest_mock
from fastapi.testclient import TestClient
from main import app
import uuid
import io

client = TestClient(app)


def test_upload_endpoint(mocker):
    # Mock für Datenbankfunktionen
    mocker.patch("app.services.file_upload_handler.save_encrypted_file", return_value=uuid.uuid4())
    mocker.patch("app.services.file_upload_handler.save_aesgcm_key")

    # Testdatei erstellen
    test_file = io.BytesIO(b"Test PDF content")

    # API-Anfrage senden
    response = client.post(
        "/api/v1/upload/",
        files={"file": ("test.pdf", test_file, "application/pdf")}
    )

    # Überprüfungen
    assert response.status_code == 200
    assert response.json() == {"message": "success"}