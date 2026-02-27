import datetime
import os
import subprocess

from config import GALLERY_DIR, STREAMS_DIR
from fastapi import HTTPException


class MediaService:
    @staticmethod
    def capture_image():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{timestamp}.jpg"
        filepath = os.path.join(GALLERY_DIR, filename)
        m3u8_path = os.path.join(STREAMS_DIR, "stream.m3u8")

        # Method 1: Try to grab a frame from the existing HLS stream
        stream_active = os.system("systemctl is-active birdfeeder-stream.service >/dev/null 2>&1") == 0
        if stream_active or os.path.exists(m3u8_path):
            # 1a. Attempt ffmpeg from the playlist
            if os.path.exists(m3u8_path):
                try:
                    result = subprocess.run(
                        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                         "-live_start_index", "-1", "-i", m3u8_path,
                         "-frames:v", "1", "-q:v", "2", filepath],
                        capture_output=True, text=True, timeout=15
                    )
                    if result.returncode == 0 and os.path.exists(filepath):
                        return {"status": "success", "filename": filename, "timestamp": timestamp,
                                "method": "stream_capture_playlist"}
                except Exception as e:
                    print(f"Stream playlist capture failed: {e}")

            # 1b. Fallback: Try to grab from the latest .ts segment directly
            try:
                ts_files = sorted([f for f in os.listdir(STREAMS_DIR) if f.endswith(".ts")], reverse=True)
                if ts_files:
                    latest_ts = os.path.join(STREAMS_DIR, ts_files[0])
                    result = subprocess.run(
                        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                         "-i", latest_ts, "-frames:v", "1", "-q:v", "2", filepath],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0 and os.path.exists(filepath):
                        return {"status": "success", "filename": filename, "timestamp": timestamp,
                                "method": "stream_capture_direct_segment"}
            except Exception as e:
                print(f"Stream segment capture failed: {e}")

        # Method 2: Fallback to rpicam-still (ONLY if stream is NOT running)
        if stream_active:
            raise HTTPException(status_code=500,
                                detail="Failed to capture from active stream. Camera is busy and HLS capture failed.")

        try:
            result = subprocess.run(
                ["rpicam-still", "-o", filepath, "--nopreview", "-t", "1000"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                raise HTTPException(status_code=500, detail=f"Capture failed: {result.stderr}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

        return {"status": "success", "filename": filename, "timestamp": timestamp, "method": "rpicam-still"}

    @staticmethod
    def capture_clip():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clip_{timestamp}.mp4"
        filepath = os.path.join(GALLERY_DIR, filename)
        m3u8_path = os.path.join(STREAMS_DIR, "stream.m3u8")

        # Method 1: Try to grab the last 10 seconds from the HLS stream
        stream_active = os.system("systemctl is-active birdfeeder-stream.service >/dev/null 2>&1") == 0
        if stream_active or os.path.exists(m3u8_path):
            # 1a. Attempt ffmpeg from the playlist
            if os.path.exists(m3u8_path):
                try:
                    result = subprocess.run(
                        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                         "-sseof", "-10", "-i", m3u8_path, "-c", "copy", filepath],
                        capture_output=True, text=True, timeout=20
                    )
                    if result.returncode == 0 and os.path.exists(filepath):
                        return {"status": "success", "filename": filename, "timestamp": timestamp,
                                "method": "stream_clip_playlist"}
                except Exception as e:
                    print(f"Stream playlist clip capture failed: {e}")

            # 1b. Fallback: Try to concatenate the last few .ts segments directly
            try:
                ts_files = sorted([f for f in os.listdir(STREAMS_DIR) if f.endswith(".ts")], reverse=True)
                # Take up to 12 segments (assuming 1s each, slightly more than 10s to be safe)
                recent_ts = sorted(ts_files[:12])
                if recent_ts:
                    # Create a concat list for ffmpeg
                    concat_file = os.path.join(STREAMS_DIR, f"concat_{timestamp}.txt")
                    with open(concat_file, "w") as f:
                        for ts in recent_ts:
                            f.write(f"file '{ts}'\n")

                    result = subprocess.run(
                        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                         "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", filepath],
                        capture_output=True, text=True, timeout=15
                    )
                    os.remove(concat_file)
                    if result.returncode == 0 and os.path.exists(filepath):
                        return {"status": "success", "filename": filename, "timestamp": timestamp,
                                "method": "stream_clip_direct_concat"}
            except Exception as e:
                print(f"Stream segment concat failed: {e}")

        # Method 2: Fallback to rpicam-vid (ONLY if stream is NOT running)
        if stream_active:
            raise HTTPException(status_code=500,
                                detail="Failed to capture clip from active stream. Camera is busy and HLS capture failed.")

        try:
            h264_tmp = filepath.replace(".mp4", ".h264")
            result = subprocess.run(
                ["rpicam-vid", "-t", "10000", "-o", h264_tmp, "--nopreview"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                if os.path.exists(h264_tmp): os.remove(h264_tmp)
                raise HTTPException(status_code=500, detail=f"Clip capture failed: {result.stderr}")

            subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", h264_tmp, "-c", "copy", filepath],
                capture_output=True, text=True, timeout=10
            )
            if os.path.exists(h264_tmp): os.remove(h264_tmp)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

        return {"status": "success", "filename": filename, "timestamp": timestamp, "method": "rpicam-vid"}

    @staticmethod
    def list_gallery():
        try:
            files = [f for f in os.listdir(GALLERY_DIR) if f.endswith(".jpg") or f.endswith(".mp4")]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(GALLERY_DIR, x)), reverse=True)
            return files
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing gallery: {e}")

    @staticmethod
    def delete_media(filename: str):
        try:
            filepath = os.path.join(GALLERY_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting media: {e}")
