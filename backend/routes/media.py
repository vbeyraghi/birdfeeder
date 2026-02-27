import os

from config import GALLERY_DIR
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.media_service import MediaService

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/capture")
def capture_image():
    return MediaService.capture_image()


@router.post("/clip")
def capture_clip():
    return MediaService.capture_clip()


@router.get("/gallery")
def list_gallery():
    return MediaService.list_gallery()


@router.get("/gallery/{filename}")
def get_media(filename: str):
    """Serves a specific image or video from the gallery."""
    filepath = os.path.join(GALLERY_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Media not found")

    media_type = "image/jpeg"
    if filename.endswith(".mp4"):
        media_type = "video/mp4"

    return FileResponse(filepath, media_type=media_type)


@router.delete("/gallery/{filename}")
def delete_media(filename: str):
    """Deletes a specific media file from the gallery."""
    success = MediaService.delete_media(filename)
    if not success:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"status": "success", "message": f"Deleted {filename}"}
