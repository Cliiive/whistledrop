from fastapi import FastAPI
from contextlib import asynccontextmanager
# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.user import router as user_router
from app.api.v1.upload import router as upload_router

from app.db.session import create_tables
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("App starting up...")
    try:
        create_tables()
        print("Tables created successfully")
    except Exception as e:
        print(f"Fehler beim Erstellen der Tabellen: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router, prefix="/api/v1/user")
app.include_router(upload_router, prefix="/api/v1/upload")