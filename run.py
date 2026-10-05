"""
ComicCraft - Runner Script
Launch the application with: python run.py
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Ensure comiccraft directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"Starting ComicCraft on http://{host}:{port}...")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
