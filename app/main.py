"""
ComicCraft - FastAPI Application Entrypoint
Main server setup, static file mounting, router registration, and lifecycle management.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler: ensures directories exist on startup."""
    # Ensure all required directories exist
    required_dirs = [
        os.path.join(STATIC_DIR, "panels"),
        os.path.join(STATIC_DIR, "exports"),
        os.path.join(STATIC_DIR, "fonts"),
        os.path.join(STATIC_DIR, "images"),
        os.path.join(STATIC_DIR, "css"),
        os.path.join(STATIC_DIR, "js"),
    ]
    for d in required_dirs:
        os.makedirs(d, exist_ok=True)

    print("=======================================================")
    print(" [READY] ComicCraft - AI Comic Story Creator is Running!")
    print(f" [*] Static Assets: {STATIC_DIR}")
    print(" [*] App Homepage:  http://127.0.0.1:8000")
    print(" [*] API Swagger:   http://127.0.0.1:8000/docs")
    print("=======================================================")
    yield


app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Full-stack AI comic book generator utilizing Google Gemini Models and Stable Diffusion.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin client apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include routes
from app.routes import router
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
