from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_user_creation_login_upload_and_view():
    # Test Benutzererstellung
    response = client.get("/api/v1/auth/register")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "passphrase" in data
    assert "access_token" in data
    user_id = data["user_id"]
    passphrase = data["passphrase"]
    access_token = data["access_token"]

    # Test Login
    login_response = client.post("/api/v1/auth/login", json={"passphrase": passphrase})
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["user_id"] == user_id
    assert "access_token" in login_data

    # Setze den Authorization-Header für den nächsten Schritt
    headers = {"Authorization": f"Bearer {login_data['access_token']}"}

    # Test Datei-Upload
    file_content = b"%PDF-1.4\n%Test PDF content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    upload_response = client.post("/api/v1/upload/", files=files, headers=headers)
    assert upload_response.status_code == 200
    assert upload_response.json()["message"] == "success"

    # Test Anzeigen hochgeladener Dateien
    files_response = client.get("/api/v1/upload/", headers=headers)
    assert files_response.status_code == 200
    uploaded_files = files_response.json()
    assert len(uploaded_files) > 0
    assert uploaded_files[0]["file_name"] == "test_encrypted"

    # Remove the uploaded file
    file_id = uploaded_files[0]["id"]
    delete_response = client.delete(f"/api/v1/upload/{file_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "File deleted successfully"

    # Check if the file is actually deleted
    files_response_after_delete = client.get("/api/v1/upload/", headers=headers)
    assert files_response_after_delete.status_code == 200
    uploaded_files_after_delete = files_response_after_delete.json()
    assert len(uploaded_files_after_delete) == 0


