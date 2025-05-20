#Bib. dotenv
import os
import sqlite3
import requests
from dotenv import load_dotenv
load_dotenv()  # .env-Datei laden


DATABASE_URL_ADMIN = os.getenv("DATABASE_REMOTE_URL_ADMIN")
#print("Datenbankpfad:", datenbankpfad)


def get_public_keys():
    conn = sqlite3.connect("../meine_datenbank.db")
    cursor = conn.cursor()

    # Nur die gewünschte Spalte abfragen
    cursor.execute("SELECT public_key, id FROM schluesselpaare WHERE uploaded == False")

    # Alle Zeilen holen (jede ist ein Tupel mit einem Element)
    rows = cursor.fetchall()

    # Jeder Key kann str oder bytes sein, wir stellen sicher dass es bytes sind
    public_keys = [row[0].encode("utf-8") if isinstance(row[0], str) else row[0] for row in rows]
    ids = [row[1] for row in rows]
    conn.close()
    return public_keys,ids

def update_local_database():
    conn = sqlite3.connect("../meine_datenbank.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE schluesselpaare SET uploaded = True WHERE uploaded == False")
    conn.commit()
    conn.close()

def create_temp_key_file(key, index, directory="temp_keys"):
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, f"public_key_{index}.pem")
    with open(filename, "wb") as f:
        f.write(key)
    return filename

def upload_key_file(filepath, token, tor_post, key_id=None, ):
    # URL of the server endpoint

    # Data to be sent in the LOGIN_POST reques
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Open file and send
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f, "application/x-pem-file")}
        response = tor_post("/publickey/" + str(key_id), files=files, headers=headers)
        print("Antwort:", response.text)

if __name__ == '__main__':
    keys, ids = get_public_keys()

    print(f"{len(keys)} Schlüssel gefunden.")
    for index, key in enumerate(keys):
        filename = create_temp_key_file(key, index)
        upload_key_file(filename, ids[index])






