#Lib. cryptography
import uuid
import argparse
import sqlite3
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keys(key_size: int):
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

    # Serialize private key to PEM format
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Generate and serialize public key
    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    print("RSA key pair successfully generated.")
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
    # Connection to SQLite database (file is created if it doesn't exist)
    conn = sqlite3.connect("../meine_datenbank.db")
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schluesselpaare (
            id TEXT PRIMARY KEY,
            public_key TEXT NOT NULL,
            private_key TEXT NOT NULL,
            uploaded BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)

    for key_pair in keys:
        cursor.execute("""
                   INSERT INTO schluesselpaare (id, private_key, public_key, uploaded)
                   VALUES (?, ?, ?, ?)
                   """, (str(uuid.uuid4()), key_pair[0], key_pair[1], False))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates multiple RSA key pairs.")

    parser.add_argument(
        "-n", "--number",
        type=int,
        default=1,
        help="Number of key pairs (default: 1)"
    )

    parser.add_argument(
        "-s", "--size",
        type=int,
        default=2048,
        help="Key length in bits (default: 2048)"
    )

    args = parser.parse_args()

    #print("Number: ", args.number, " | Size of Key: ", args.size)
    key = generate_multiple_keys(count=args.number, key_size=args.size)
    
    write_keys_to_database(keys = key)
