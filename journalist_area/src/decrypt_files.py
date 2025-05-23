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

DATABASE_PATH = "./meine_datenbank.db"
DEFAULT_INPUT_DIR = "./downloads"
DEFAULT_OUTPUT_DIR = "./decrypted_files"

def load_private_key_from_db(public_key_id):
    """Loads the private key from the database based on the ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT private_key FROM schluesselpaare 
        WHERE id = ?
    """, (public_key_id,))
    
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise ValueError(f"No private key found for ID {public_key_id}!")
    
    private_key_pem = result[0]
    private_key = load_pem_private_key(
        private_key_pem,
        password=None
    )
    
    return private_key


def decrypt_aes_key(encrypted_key, private_key):
    """Decrypts an AES key with a private RSA key."""
    try:
        # Remove all whitespaces and line breaks

        # Base64-decode the encrypted key
        encrypted_key_bytes = b64decode(encrypted_key)
        # Check lengths
        key_size_bytes = private_key.key_size // 8
        if len(encrypted_key_bytes) != key_size_bytes:
            print(
                f"Warning: Ciphertext length ({len(encrypted_key_bytes)}) does not match key size ({key_size_bytes})")

        # Decrypt the AES key with the private RSA key
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
        print(f"Error decrypting AES key: {e}")
        raise

def decrypt_file(encrypted_file_path, aes_key, nonce, output_file_path):
    """Decrypts a file with AES-GCM."""
    try:
        # Read the encrypted file
        with open(encrypted_file_path , 'rb') as file:
            encrypted_data = file.read()
        
        # Decrypt with AES-GCM
        aesgcm = AESGCM(aes_key)
        decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
        
        # Write the decrypted file
        with open(output_file_path, 'wb') as file:
            file.write(decrypted_data)
            
        return True
    except Exception as e:
        print(f"Error decrypting {encrypted_file_path}: {str(e)}")
        return False

def process_files(input_dir, output_dir):
    """Processes all files in the input directory."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all file pairs (file and associated key_info.txt)
    success_count = 0
    error_count = 0
    
    # Collect all files without the key_info.txt files
    files = [f for f in os.listdir(input_dir) 
             if os.path.isfile(os.path.join(input_dir, f)) and not f.endswith('_key_info.txt')]
    
    for filename in files:
        try:
            file_path = os.path.join(input_dir, filename)
            file_id = filename.split('_')[0]  # Extract the file ID
            key_info_path = os.path.join(input_dir, f"{file_id}_key_info.txt")
            
            if not os.path.exists(key_info_path):
                print(f"Key info for {filename} not found!")
                error_count += 1
                continue
            
            # Read the key info
            with open(key_info_path, 'r') as key_file:
                key_info = key_file.read()
            
            # Extract encrypted key and Public Key ID
            key_lines = key_info.split('\n')
            encrypted_key = key_lines[0].replace("Encrypted Key: ", "")
            nonce = key_lines[1].replace("Nonce: ", "")
            public_key_id = key_lines[2].replace("Public Key ID: ", "")
            # Here begins the special part for SQLite
            # Load the private key
            private_key = load_private_key_from_db(public_key_id)

            # Safe alternative to eval() for strings containing Python literals
            import ast
            try:
                encrypted_key = ast.literal_eval(encrypted_key)
                nonce = ast.literal_eval(nonce)
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing key data: {e}")
                raise

            # Decrypt the AES key
            aes_key = decrypt_aes_key(encrypted_key, private_key)
            print(f"Decrypted AES key: {aes_key}")
            # Create the output path
            original_filename = '_'.join(filename.split('_')[1:])
            output_file_path = os.path.join(output_dir, original_filename)
            
            # Decrypt the file
            if decrypt_file(file_path, aes_key, nonce, output_file_path + ".pdf"):
                success_count += 1
                print(f"File successfully decrypted: {output_file_path}")
            else:
                error_count += 1
        
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            error_count += 1
    
    print(f"\nSummary:")
    print(f"Successfully decrypted: {success_count} files")
    print(f"Errors: {error_count} files")
    return success_count, error_count

def decrypt_all():
    # parser = argparse.ArgumentParser(description="Decrypts files with RSA private keys and AES.")
    #
    # parser.add_argument(
    #     "-i", "--input",
    #     default=DEFAULT_INPUT_DIR,
    #     help=f"Input directory with encrypted files (default: {DEFAULT_INPUT_DIR})"
    # )
    #
    # parser.add_argument(
    #     "-o", "--output",
    #     default=DEFAULT_OUTPUT_DIR,
    #     help=f"Output directory for decrypted files (default: {DEFAULT_OUTPUT_DIR})"
    # )
    #
    # args = parser.parse_args()
    #
    print(f"Decrypting files from ./downloads to ./decrypted_files")
    process_files(DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR)
