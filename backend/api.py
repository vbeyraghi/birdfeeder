import csv
import datetime
import os
import subprocess
import sys
from typing import List

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add the repository root to the python path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    LOG_DIR, GALLERY_DIR, LATEST_BATTERY_CSV, API_HOST, API_PORT
)

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


class BatteryData(BaseModel):
    timestamp: str
    percentage: float
    solar_radiation_Wm2: float


@app.get("/api/battery", response_model=List[BatteryData])
def get_battery_data():
    """Returns the latest battery data from the CSV file."""
    if not os.path.exists(LATEST_BATTERY_CSV):
        return []

    data = []
    try:
        with open(LATEST_BATTERY_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(BatteryData(
                    timestamp=row["timestamp"],
                    percentage=float(row["percentage"]),
                    solar_radiation_Wm2=float(row["solar_radiation_Wm2"])
                ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading battery data: {e}")

    return data


@app.post("/api/capture")
def capture_image():
    """Takes a picture using rpicam-still and saves it to the gallery."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.jpg"
    filepath = os.path.join(GALLERY_DIR, filename)

    # Check if streaming is active (rpicam-vid might be using the camera)
    # On Raspberry Pi, multiple apps can sometimes share the camera depending on the driver,
    # but often they conflict. We might need to handle this.
    # For now, we try to capture.

    try:
        # Use rpicam-still to capture a high-quality image
        # --immediate might be faster, but let's go with defaults for better quality
        # --nopreview to avoid GUI issues
        result = subprocess.run(
            ["rpicam-still", "-o", filepath, "--nopreview", "-t", "1000"],
            capture_output=True, text=True, timeout=10
        )

        if result.returncode != 0:
            # If rpicam-still failed, it might be because the camera is busy with the stream
            raise HTTPException(status_code=500, detail=f"Capture failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Capture timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    return {"status": "success", "filename": filename, "timestamp": timestamp}


@app.get("/api/gallery")
def list_gallery():
    """Lists all captured images in the gallery, sorted by newest first."""
    try:
        files = [f for f in os.listdir(GALLERY_DIR) if f.endswith(".jpg")]
        # Sort by creation time (newest first)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(GALLERY_DIR, x)), reverse=True)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing gallery: {e}")


@app.get("/api/gallery/{filename}")
def get_image(filename: str):
    """Serves a specific image from the gallery."""
    filepath = os.path.join(GALLERY_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(filepath, media_type="image/jpeg")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=API_HOST, port=API_PORT)
