from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .routers import auth
from .db import Base, engine
from . import models

app = FastAPI(title="FastAPI Auth", version="0.1.0")

# CORS: permitir orígenes desde env (Render/Vercel) o defaults de desarrollo
_cors_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
_cors_list = [o.strip() for o in _cors_env.split(",") if o.strip()]
default_cors = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_list or default_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])

@app.get("/")
def root():
    return {
        "service": "FastAPI Auth",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/test-face-processing")
def test_face_processing():
    """Endpoint de prueba para verificar que el procesamiento facial funciona"""
    try:
        from .security import compute_face_hash_from_base64
        # Probar con una imagen base64 de prueba (puede ser cualquier imagen válida)
        test_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        face_hash = compute_face_hash_from_base64(test_image)
        return {
            "status": "ok",
            "face_processing_works": True,
            "hash_length": len(face_hash) if face_hash else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "face_processing_works": False,
            "error": str(e)
        }


@app.on_event("startup")
def on_startup():
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
