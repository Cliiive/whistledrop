from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_whole_auth_cycle(mocker):

    # Step 1: User registration
    response = client.get(
        "/api/v1/auth/register/")
    response_json = response.json()
    assert response.status_code == 200
    assert "passphrase" in response_json
    assert "user_id" in response_json

    passphrase = response_json["passphrase"]

    # Step 2: User login
    login_response = client.post(
        "/api/v1/auth/login/",
        json={"passphrase": passphrase}
    )
    login_response_json = login_response.json()
    assert login_response.status_code == 200
    assert "access_token" in login_response_json
    assert "user_id" in login_response_json


def test_wrong_phrase(mocker):
    # Mock für Datenbankfunktionen
    mocker.patch("app.services.auth_service.authenticate_user", return_value=None)

    # Testen der ungültigen Seed-Phrase
    response = client.post(
        "/api/v1/auth/login/",
        json={"passphrase": "wrong_passphrase"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Passphrase"}