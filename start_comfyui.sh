#!/bin/bash
# Start ComfyUI server for HuggingFace Spaces

# Set default port
PORT=${PORT:-8000}

# Start ComfyUI
cd /app
python main.py --listen 0.0.0.0 --port $PORT &

# Wait for server to be ready
sleep 10

# Keep script running
wait

