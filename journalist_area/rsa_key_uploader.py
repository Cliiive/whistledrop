#Bib. dotenv
import os
import sqlite3
import requests

from dotenv import load_dotenv
load_dotenv()  # .env-Datei laden


DATABASE_URL_ADMIN = os.getenv("DATABASE_REMOTE_URL_ADMIN")
#print("Datenbankpfad:", datenbankpfad)


def get_public_keys():
    conn = sqlite3.connect("meine_datenbank.db")
    cursor = conn.cursor()

    # Nur die gewünschte Spalte abfragen
    cursor.execute("SELECT private_key FROM schluesselpaare")

    # Alle Zeilen holen (jede ist ein Tupel mit einem Element)
    rows = cursor.fetchall()

    # Jeder Key kann str oder bytes sein, wir stellen sicher dass es bytes sind
    public_keys = [row[0].encode("utf-8") if isinstance(row[0], str) else row[0] for row in rows]

    conn.close()
    return public_keys

def create_temp_key_file(key, index, directory="temp_keys"):
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"public_key_{index}.pem")
    with open(filename, "wb") as f:
        f.write(key)
    return filename

def upload_key_file(filepath):
    # URL of the server endpoint
    login_url = "http://localhost:8000/api/v1/auth/login"
    upload_url = "http://localhost:8000/api/v1/publickey/"

    # Data to be sent in the LOGIN_POST request
    login_data = {"passphrase": "admin_password"}

    # Send the POST request
    login_response = requests.post(login_url, json=login_data)
    print(login_response.json())

    if login_response.status_code != 200:
        print("Login fehlgeschlagen:", login_response.text)
        return

    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    # Open file and send
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f, "application/x-pem-file")}
        response = requests.post(upload_url, files=files, headers=headers)
        print("Antwort:", response.text)

if __name__ == '__main__':
    keys = get_public_keys()

    print(f"{len(keys)} Schlüssel gefunden.")
    for index, key in enumerate(keys):
        filename = create_temp_key_file(key, index)
        upload_key_file(filename)






