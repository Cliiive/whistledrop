from fastapi import FastAPI
from contextlib import asynccontextmanager
# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.user import router as user_router
from app.api.v1.upload import router as upload_router
from app.api.v1.auth import router as auth_router
from app.api.v1.download import router as download_router
from app.api.v1.rsa_upload import router as public_key_router
from app.core.config import settings
from app.db.session import init_db
from app.db.session import init_db, create_admin_account

app = FastAPI()

# @app.on_event("startup")
# async def startup_event():
#     print("App starting up...")
#     try:
#         init_db()
#         print("Tables created successfully")
#     except Exception as e:
#         print(f"Fehler beim Erstellen der Tabellen: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# init_db()
# create_admin_account()

app.include_router(user_router, prefix=settings.API_PREFIX + "/user")
app.include_router(upload_router, prefix=settings.API_PREFIX + "/upload")
app.include_router(auth_router, prefix=settings.API_PREFIX + "/auth")
app.include_router(public_key_router, prefix=settings.API_PREFIX + "/publickey")
app.include_router(download_router, prefix=settings.API_PREFIX + "/download")

if __name__ == "__main__":
    import sys
    import uvicorn

    if "--createadmin" in sys.argv:
        idx = sys.argv.index("--createadmin")
        try:
            passphrase = sys.argv[idx + 1]
        except IndexError:
            print("ussage: --createadmin <passphrase>")
            sys.exit(1)

        from app.db.session import create_admin_account
        create_admin_account(passphrase)
        print(f"Admin was created successfully.")
    if "--init" in sys.argv:
        init_db()
        print(f"database was initialized successfully.")
    else:
        print("Normal start")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)