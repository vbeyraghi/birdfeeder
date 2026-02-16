#!/bin/bash

# Ensure the streams directory exists
cd "$(dirname "$0")"
mkdir -p ./streams

echo "Starting battery monitoring..."
source /home/beyragva/birdfeeder/battery-env/bin/activate
python3 battery_status.py &
BATTERY_PID=$!

echo "Starting CORS-enabled HTTP server..."
python3 cors_http_server.py &
CORS_PID=$!

echo "Starting Angular app HTTP server on port 8081..."
/usr/local/bin/http-server "./browser" -p 8081 &
HTTP_PID=$!

cleanup() {
  echo "Stopping servers..."
  kill $CORS_PID $HTTP_PID $BATTERY_PID 2>/dev/null

  echo "Removing streams directory..."
  rm -rf ./streams
}

# Trap CTRL+C (SIGINT) and EXIT
trap cleanup SIGINT EXIT

echo "Starting rpicam-vid and piping to ffmpeg for HLS output..."
rpicam-vid -t 0 --inline -o - | ffmpeg \
  -fflags nobuffer \
  -flags low_delay \
  -strict experimental \
  -analyzeduration 0 \
  -probesize 32 \
  -i - \
  -c:v copy \
  -f hls \
  -hls_time 1 \
  -hls_list_size 3 \
  -hls_flags delete_segments+append_list+omit_endlist+program_date_time \
  -hls_allow_cache 0 \
  ./streams/stream.m3u8