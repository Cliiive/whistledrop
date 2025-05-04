from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def gen_aesgcm() -> AESGCM:
    # Generates a cryptographically secure 256-bit key
    key: bytes = AESGCM.generate_key(256)
    print("New aesgcm key generated")
    return AESGCM(key)

def encrypt_pdf(pdf_path: str) -> tuple[bytes, bytes]:
    # Encrypts the PDF file at the given path using the provided AESGCM key
    aesgcm = gen_aesgcm()
    with open(pdf_path, "rb") as f:
        plain_data = f.read()

    nonce = os.urandom(12)  # Generate a random nonce

    ciphertext = aesgcm.encrypt(nonce, plain_data, associated_data=None)

    return nonce, ciphertext