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

# Load video configuration if it exists, otherwise use defaults
if [ -f "./video_config.sh" ]; then
  source ./video_config.sh
else
  WIDTH=1920
  HEIGHT=1080
  FRAMERATE=30
  BITRATE=2500000
fi

echo "Starting rpicam-vid → ffmpeg (${WIDTH}x${HEIGHT}@${FRAMERATE}fps, ${BITRATE}bps)"
rpicam-vid \
  -t 0 \
  --width ${WIDTH} --height ${HEIGHT} \
  --framerate ${FRAMERATE} \
  --bitrate ${BITRATE} \
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
  -hls_list_size 3 \
  -hls_delete_threshold 1 \
  -hls_flags delete_segments+append_list+omit_endlist+independent_segments+temp_file \
  -hls_allow_cache 0 \
  -hls_segment_filename "./streams/seg_%05d.ts" \
  ./streams/stream.m3u8