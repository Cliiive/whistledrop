# backend/tests/test_upload_api.py
import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient

from app.services.file_upload_handler import encrypt_pdf, save_encrypted_file, save_aesgcm_key
from main import app
import uuid
import io
import os

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


# Einheitentests
def test_encrypt_pdf():
    # Testdatei erstellen
    test_content = b"Test PDF content"
    test_file = io.BytesIO(test_content)
    test_file.filename = "test_encrypt.pdf"

    file = UploadFile(file=test_file, filename="test_encrypt.pdf")

    # Funktion aufrufen
    result = encrypt_pdf(file)

    # Überprüfungen
    assert result.file_name == "test_encrypt.pdf"
    assert isinstance(result.ciphertext, bytes)
    assert len(result.ciphertext) > 0
    assert isinstance(result.nonce, bytes)
    assert len(result.nonce) == 12
    assert isinstance(result.key, bytes)
    assert len(result.key) == 32  # 256 Bit = 32 Bytes


def test_save_encrypted_file(mocker):
    # Mock für Datenbankoperationen
    mock_db = mocker.MagicMock()
    mock_db.commit = mocker.MagicMock()
    mock_db.refresh = mocker.MagicMock()
    mock_db.add = mocker.MagicMock()

    # Mock für den Dateisystemzugriff
    mocker.patch("os.makedirs")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.path.exists", return_value=False)

    # Mock für die Benutzereinführung
    mocker.patch("app.services.file_upload_handler.insert_random_user", return_value=uuid.uuid4())

    # Funktion aufrufen
    file_id = save_encrypted_file(mock_db, "test_file.pdf", b"encrypted_content")

    # Überprüfungen
    assert isinstance(file_id, uuid.UUID)
    mock_open.assert_called_once()
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called()


def test_save_aesgcm_key(mocker):
    # Mock für Datenbankoperationen
    mock_db = mocker.MagicMock()
    mock_db.commit = mocker.MagicMock()
    mock_db.refresh = mocker.MagicMock()
    mock_db.add = mocker.MagicMock()

    # Testdaten
    test_key = os.urandom(32)
    test_file_id = uuid.uuid4()
    test_nonce = os.urandom(12)

    # Funktion aufrufen
    save_aesgcm_key(mock_db, test_key, test_file_id, test_nonce)

    # Überprüfungen
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


# Edge Cases
def test_upload_empty_file(mocker):
    # Mocks konfigurieren
    mocker.patch("app.services.file_upload_handler.save_encrypted_file", return_value=uuid.uuid4())
    mocker.patch("app.services.file_upload_handler.save_aesgcm_key")

    # Leere Datei erstellen
    empty_file = io.BytesIO(b"")

    # API-Anfrage senden
    response = client.post(
        "/api/v1/upload/",
        files={"file": ("empty.pdf", empty_file, "application/pdf")}
    )

    # Überprüfungen
    assert response.status_code == 200  # Sollte trotzdem erfolgreich sein


def test_upload_unsupported_file_type(mocker):
    # Testdatei erstellen
    test_file = io.BytesIO(b"Test text content")

    # API-Anfrage senden
    response = client.post(
        "/api/v1/upload/",
        files={"file": ("test.txt", test_file, "text/plain")}
    )

    assert response.status_code == 415


def test_upload_duplicate_filename(mocker):
    # Mocks für Datei-Existenz (simuliert bereits existierende Datei)
    mocker.patch("os.path.exists",
                 side_effect=[True, False])  # Erster Aufruf: Datei existiert, zweiter Aufruf: Datei existiert nicht
    mocker.patch("os.makedirs")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    # Datenbankoperationen mocken
    mock_db = mocker.MagicMock()
    file_id = uuid.uuid4()
    mocker.patch("app.services.file_upload_handler.insert_random_user", return_value=uuid.uuid4())

    # Funktion direkt aufrufen
    result = save_encrypted_file(mock_db, "duplicate.pdf", b"content")

    # Überprüfen, ob die Datei mit einem geänderten Namen gespeichert wurde
    assert "_1" in mock_open.call_args[0][0]


def test_upload_no_file():
    # API-Anfrage ohne Datei senden
    response = client.post("/api/v1/upload/")

    # Überprüfungen
    assert response.status_code != 200  # Sollte einen Fehler zurückgeben