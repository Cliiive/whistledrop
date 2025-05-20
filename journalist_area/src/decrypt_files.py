import os
import sqlite3
import argparse
import glob
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from base64 import b64decode
import shutil

DATABASE_PATH = "../../meine_datenbank.db"
DEFAULT_INPUT_DIR = "../../downloads"
DEFAULT_OUTPUT_DIR = "../../decrypted_files"

def load_private_key_from_db(public_key_id):
    """Lädt den privaten Schlüssel aus der Datenbank basierend auf der ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT private_key FROM schluesselpaare 
        WHERE id = ?
    """, (public_key_id,))
    
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise ValueError(f"Kein privater Schlüssel für ID {public_key_id} gefunden!")
    
    private_key_pem = result[0]
    private_key = load_pem_private_key(
        private_key_pem,
        password=None
    )
    
    return private_key


def decrypt_aes_key(encrypted_key, private_key):
    """Entschlüsselt einen AES-Schlüssel mit einem privaten RSA-Schlüssel."""
    try:
        # Entferne alle Whitespaces und Zeilenumbrüche

        # Base64-decodieren des verschlüsselten Schlüssels
        encrypted_key_bytes = b64decode(encrypted_key)
        # Prüfe Längen
        key_size_bytes = private_key.key_size // 8
        if len(encrypted_key_bytes) != key_size_bytes:
            print(
                f"Warnung: Ciphertext-Länge ({len(encrypted_key_bytes)}) stimmt nicht mit Schlüsselgröße ({key_size_bytes}) überein")

        # Entschlüsseln des AES-Schlüssels mit dem privaten RSA-Schlüssel
        decrypted_key = private_key.decrypt(
            encrypted_key_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return decrypted_key
    except Exception as e:
        print(f"Fehler beim Entschlüsseln des AES-Schlüssels: {e}")
        raise

def decrypt_file(encrypted_file_path, aes_key, nonce, output_file_path):
    """Entschlüsselt eine Datei mit AES-GCM."""
    try:
        # Lese die verschlüsselte Datei
        with open(encrypted_file_path , 'rb') as file:
            encrypted_data = file.read()
        
        # Entschlüsseln mit AES-GCM
        aesgcm = AESGCM(aes_key)
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
        
        # Schreibe die entschlüsselte Datei
        with open(output_file_path, 'wb') as file:
            file.write(decrypted_data)
            
        return True
    except Exception as e:
        print(f"Fehler beim Entschlüsseln von {encrypted_file_path}: {str(e)}")
        return False

def process_files(input_dir, output_dir):
    """Verarbeitet alle Dateien im Eingabeverzeichnis."""
    # Stelle sicher, dass das Ausgabeverzeichnis existiert
    os.makedirs(output_dir, exist_ok=True)
    
    # Finde alle Dateipaare (Datei und dazugehörige key_info.txt)
    success_count = 0
    error_count = 0
    
    # Sammle alle Dateien ohne die key_info.txt-Dateien
    files = [f for f in os.listdir(input_dir) 
             if os.path.isfile(os.path.join(input_dir, f)) and not f.endswith('_key_info.txt')]
    
    for filename in files:
        try:
            file_path = os.path.join(input_dir, filename)
            file_id = filename.split('_')[0]  # Extrahiere die Datei-ID
            key_info_path = os.path.join(input_dir, f"{file_id}_key_info.txt")
            
            if not os.path.exists(key_info_path):
                print(f"Schlüsselinfo für {filename} nicht gefunden!")
                error_count += 1
                continue
            
            # Lese die Schlüsselinfos
            with open(key_info_path, 'r') as key_file:
                key_info = key_file.read()
            
            # Extrahiere verschlüsselten Schlüssel und Public Key ID
            key_lines = key_info.split('\n')
            encrypted_key = key_lines[0].replace("Encrypted Key: ", "")
            nonce = key_lines[1].replace("Nonce: ", "")
            public_key_id = key_lines[2].replace("Public Key ID: ", "")
            # Hier beginnt der spezielle Teil für SQLite
            # Lade den privaten Schlüssel
            private_key = load_private_key_from_db(public_key_id)

            # Sichere Alternative zu eval() für Strings, die Python-Literale enthalten
            import ast
            try:
                encrypted_key = ast.literal_eval(encrypted_key)
                nonce = ast.literal_eval(nonce)
            except (ValueError, SyntaxError) as e:
                print(f"Fehler beim Parsen der Schlüsseldaten: {e}")
                raise

            # Entschlüssele den AES-Schlüssel
            aes_key = decrypt_aes_key(encrypted_key, private_key)
            print(f"Entschlüsselter AES-Schlüssel: {aes_key}")
            # Erzeuge den Ausgabepfad
            original_filename = '_'.join(filename.split('_')[1:])
            output_file_path = os.path.join(output_dir, original_filename)
            
            # Entschlüssele die Datei
            if decrypt_file(file_path, aes_key, nonce, output_file_path + ".pdf"):
                success_count += 1
                print(f"Datei erfolgreich entschlüsselt: {output_file_path}")
            else:
                error_count += 1
        
        except Exception as e:
            print(f"Fehler bei Verarbeitung von {filename}: {str(e)}")
            error_count += 1
    
    print(f"\nZusammenfassung:")
    print(f"Erfolgreich entschlüsselt: {success_count} Dateien")
    print(f"Fehler: {error_count} Dateien")
    return success_count, error_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entschlüsselt Dateien mit RSA-privaten Schlüsseln und AES.")
    
    parser.add_argument(
        "-i", "--input",
        default=DEFAULT_INPUT_DIR,
        help=f"Eingabeverzeichnis mit verschlüsselten Dateien (Standard: {DEFAULT_INPUT_DIR})"
    )
    
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Ausgabeverzeichnis für entschlüsselte Dateien (Standard: {DEFAULT_OUTPUT_DIR})"
    )
    
    args = parser.parse_args()
    
    print(f"Entschlüssele Dateien aus {args.input} nach {args.output}")
    process_files(args.input, args.output)
