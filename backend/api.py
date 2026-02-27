import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the repository root to the python path so we can import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from routes import battery, media
from config import API_HOST, API_PORT, GALLERY_DIR

app = FastAPI(title="BirdFeeder Backend")

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure gallery directory exists
os.makedirs(GALLERY_DIR, exist_ok=True)

# Include routers
app.include_router(battery.router, prefix="/api")
app.include_router(media.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=API_HOST, port=API_PORT)
