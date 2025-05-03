from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

app = FastAPI()

# Allow React frontend to talk to FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/api/v1")
async def test_response():
    import base64
    try:
        aes_key = gen_aesgcm()

        # TODO: Encypt + Store the key in a secure way

        nonve, cypher = encrypt_pdf("./test.pdf", aes_key)

        # TODO: Store the encrypted PDF in a secure way

        print("Successfully encrypted PDF")
        return {"message": "Successfully encrypted PDF"}
    except Exception as error:
        print("Error: ", error)
        return {"message": "Internal Server Error"}

def gen_aesgcm() -> AESGCM:
    # Generates a cryptographically secure 256-bit key
    key: bytes = AESGCM.generate_key(256)
    print("New aesgcm key generated")
    return AESGCM(key)

def encrypt_pdf(pdf_path: str, aesgcm: AESGCM) -> tuple[bytes, bytes]:
    # Encrypts the PDF file at the given path using the provided AESGCM key
    with open(pdf_path, "rb") as f:
        plain_data = f.read()

    nonce = os.urandom(12)  # Generate a random nonce

    ciphertext = aesgcm.encrypt(nonce, plain_data, associated_data=None)

    return nonce, ciphertext
