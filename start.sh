#!/bin/bash

# Ensure the streams directory exists
mkdir -p ./streams

echo "Starting CORS-enabled HTTP server..."
python3 cors_http_server.py &
CORS_PID=$!

echo "Starting Angular app HTTP server on port 8081..."
http-server "./browser" -p 8081 &
HTTP_PID=$!

cleanup() {
  echo "Stopping servers..."
  kill $CORS_PID $HTTP_PID 2>/dev/null

  echo "Removing streams directory..."
  rm -rf ./streams
}

# Trap CTRL+C (SIGINT) and EXIT
trap cleanup SIGINT EXIT

echo "Starting libcamera-vid and piping to ffmpeg for HLS output..."
libcamera-vid -t 0 --inline -o - | ffmpeg -fflags nobuffer -i - \
  -c:v copy \
  -f hls \
  -hls_time 2 \
  -hls_list_size 5 \
  -hls_flags delete_segments+append_list \
  ./streams/stream.m3u8
