#!/bin/bash

# Ensure the streams directory exists
cd "$(dirname "$0")"
mkdir -p ./streams

echo "Starting battery monitoring..."
source /home/beyragva/birdfeeder/battery-env/bin/activate
python3 battery_status.py &
BATTERY_PID=$!

cleanup() {
  echo "Stopping servers..."
  kill $BATTERY_PID 2>/dev/null

  echo "Removing streams directory..."
  rm -rf ./streams
}

# Trap CTRL+C (SIGINT) and EXIT
trap cleanup SIGINT EXIT

echo "Starting rpicam-vid → ffmpeg (1080p30)"
rpicam-vid \
  -t 0 \
  --width 1920 --height 1080 \
  --framerate 30 \
  --intra 60 \
  --inline \
  -o - \
| ffmpeg -hide_banner -loglevel error \
  -fflags +genpts+nobuffer \
  -flags low_delay \
  -analyzeduration 0 \
  -probesize 32 \
  -thread_queue_size 1024 \
  -i pipe:0 \
  -c:v copy \
  -muxdelay 0 -muxpreload 0 \
  -f hls \
  -hls_time 2 \
  -hls_list_size 6 \
  -hls_delete_threshold 1 \
  -hls_flags delete_segments+append_list+omit_endlist+independent_segments+temp_file \
  -hls_allow_cache 0 \
  -hls_segment_filename "./streams/seg_%05d.ts" \
  ./streams/stream.m3u8