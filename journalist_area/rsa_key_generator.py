#Bib. cryptography
import argparse
import sqlite3
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keys(key_size: int):
    # Privaten Schlüssel generieren
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

    # Privaten Schlüssel in PEM-Format serialisieren
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Öffentlichen Schlüssel generieren und serialisieren
    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    print("RSA-Schlüsselpaar erfolgreich generiert.")
    #print("Private Key: ", pem_private)
    #print("Public Key: ", pem_public)
    return pem_private, pem_public


def generate_multiple_keys(count: int, key_size: int):
    if count < 1:
        raise ValueError("Number of keys must be greater than 0.")
    keys = []
    while count > 0:
        tmp = generate_rsa_keys(key_size)
        keys.append(tmp)
        count -= 1
    return keys

def write_keys_to_database(keys: list):
    # Verbindung zur SQLite-Datenbank (Datei wird erstellt, falls sie nicht existiert)
    conn = sqlite3.connect("meine_datenbank.db")
    cursor = conn.cursor()

    # Tabelle erstellen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schluesselpaare (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            public_key TEXT NOT NULL,
            private_key TEXT NOT NULL
        )
    """)

    for key_pair in keys:
        cursor.execute("""
                   INSERT INTO schluesselpaare (private_key, public_key)
                   VALUES (?, ?)
                   """, key_pair)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generiert mehrere RSA-Schlüsselpaare.")

    parser.add_argument(
        "-n", "--number",
        type=int,
        default=1,
        help="Anzahl der Schlüsselpaare (Standard: 1)"
    )

    parser.add_argument(
        "-s", "--size",
        type=int,
        default=2048,
        help="Schlüssellänge in Bit (Standard: 2048)"
    )

    args = parser.parse_args()

    #print("Number: ", args.number, " | Size of Key: ", args.size)
    key = generate_multiple_keys(count=args.number, key_size=args.size)
    
    write_keys_to_database(keys = key)



