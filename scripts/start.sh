#!/bin/bash

# Robustly find the repository root relative to this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load video configuration if it exists, otherwise use defaults
CONFIG_FILE="$REPO_ROOT/scripts/video_config.sh"
if [ -f "$CONFIG_FILE" ]; then
  source "$CONFIG_FILE"
else
  WIDTH=1280
  HEIGHT=720
  FRAMERATE=30
  BITRATE=2500000
fi

echo "Starting rpicam-vid → ffmpeg (${WIDTH}x${HEIGHT}@${FRAMERATE}fps, ${BITRATE}bps)"
rpicam-vid \
  -t 0 \
  --width ${WIDTH} --height ${HEIGHT} \
  --framerate ${FRAMERATE} \
  --bitrate ${BITRATE} \
  --intra ${FRAMERATE} \
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
  -hls_time 1 \
  -hls_list_size 20 \
  -hls_delete_threshold 5 \
  -hls_flags delete_segments+append_list+omit_endlist+independent_segments+temp_file \
  -hls_allow_cache 0 \
  -hls_segment_filename "$REPO_ROOT/streams/seg_%05d.ts" \
  "$REPO_ROOT/streams/stream.m3u8"