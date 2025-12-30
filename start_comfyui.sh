#!/bin/bash
# Start ComfyUI backend and Gradio frontend for HuggingFace Spaces

set -e

# Configuration
COMFYUI_PORT=${COMFYUI_PORT:-8188}
GRADIO_PORT=${GRADIO_PORT:-7860}
COMFYUI_PATH=${COMFYUI_PATH:-/app/ComfyUI}

echo "=========================================="
echo "  Product Photography Generator"
echo "  Starting services..."
echo "=========================================="

# Function to download models if not present
download_models() {
    echo "[INFO] Checking for required models..."
    
    # Create model directories
    mkdir -p ${COMFYUI_PATH}/models/checkpoints
    mkdir -p ${COMFYUI_PATH}/models/clip_vision
    mkdir -p ${COMFYUI_PATH}/models/ipadapter
    mkdir -p ${COMFYUI_PATH}/models/controlnet
    
    # Check and download Juggernaut XL v9 (base model)
    if [ ! -f "${COMFYUI_PATH}/models/checkpoints/juggernautXL_v9.safetensors" ]; then
        echo "[INFO] Downloading Juggernaut XL v9..."
        python -c "
from huggingface_hub import hf_hub_download
import os
model_path = hf_hub_download(
    repo_id='RunDiffusion/Juggernaut-XL-v9',
    filename='Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors',
    local_dir='${COMFYUI_PATH}/models/checkpoints',
    local_dir_use_symlinks=False
)
os.rename(model_path, '${COMFYUI_PATH}/models/checkpoints/juggernautXL_v9.safetensors')
print('[OK] Juggernaut XL v9 downloaded')
" || echo "[WARN] Could not download Juggernaut XL v9"
    else
        echo "[OK] Juggernaut XL v9 already present"
    fi
    
    # Check and download CLIP Vision
    if [ ! -f "${COMFYUI_PATH}/models/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" ]; then
        echo "[INFO] Downloading CLIP Vision ViT-H-14..."
        python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='h94/IP-Adapter',
    filename='models/image_encoder/model.safetensors',
    local_dir='${COMFYUI_PATH}/models/clip_vision',
    local_dir_use_symlinks=False
)
import shutil
import os
src = '${COMFYUI_PATH}/models/clip_vision/models/image_encoder/model.safetensors'
dst = '${COMFYUI_PATH}/models/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors'
if os.path.exists(src):
    shutil.move(src, dst)
    shutil.rmtree('${COMFYUI_PATH}/models/clip_vision/models', ignore_errors=True)
print('[OK] CLIP Vision downloaded')
" || echo "[WARN] Could not download CLIP Vision"
    else
        echo "[OK] CLIP Vision already present"
    fi
    
    # Check and download IP-Adapter Plus SDXL
    if [ ! -f "${COMFYUI_PATH}/models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors" ]; then
        echo "[INFO] Downloading IP-Adapter Plus SDXL..."
        python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='h94/IP-Adapter',
    filename='sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors',
    local_dir='${COMFYUI_PATH}/models/ipadapter',
    local_dir_use_symlinks=False
)
import shutil
import os
src = '${COMFYUI_PATH}/models/ipadapter/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors'
dst = '${COMFYUI_PATH}/models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors'
if os.path.exists(src):
    shutil.move(src, dst)
    shutil.rmtree('${COMFYUI_PATH}/models/ipadapter/sdxl_models', ignore_errors=True)
print('[OK] IP-Adapter Plus SDXL downloaded')
" || echo "[WARN] Could not download IP-Adapter Plus SDXL"
    else
        echo "[OK] IP-Adapter Plus SDXL already present"
    fi
    
    # Check and download ControlNet Canny SDXL
    if [ ! -f "${COMFYUI_PATH}/models/controlnet/controlnet-canny-sdxl-1.0.safetensors" ]; then
        echo "[INFO] Downloading ControlNet Canny SDXL..."
        python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='xinsir/controlnet-canny-sdxl-1.0',
    filename='diffusion_pytorch_model.safetensors',
    local_dir='${COMFYUI_PATH}/models/controlnet',
    local_dir_use_symlinks=False
)
import shutil
import os
src = '${COMFYUI_PATH}/models/controlnet/diffusion_pytorch_model.safetensors'
dst = '${COMFYUI_PATH}/models/controlnet/controlnet-canny-sdxl-1.0.safetensors'
if os.path.exists(src):
    shutil.move(src, dst)
print('[OK] ControlNet Canny SDXL downloaded')
" || echo "[WARN] Could not download ControlNet Canny SDXL"
    else
        echo "[OK] ControlNet Canny SDXL already present"
    fi
    
    echo "[INFO] Model check complete"
}

# Function to wait for ComfyUI to be ready
wait_for_comfyui() {
    echo "[INFO] Waiting for ComfyUI to start..."
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "http://127.0.0.1:${COMFYUI_PORT}/system_stats" > /dev/null 2>&1; then
            echo "[OK] ComfyUI is ready!"
            return 0
        fi
        attempt=$((attempt + 1))
        echo "[INFO] Waiting for ComfyUI... ($attempt/$max_attempts)"
        sleep 2
    done
    
    echo "[WARN] ComfyUI did not start within expected time, continuing anyway..."
    return 1
}

# Download models
download_models

# Start ComfyUI in background
echo "[INFO] Starting ComfyUI on port ${COMFYUI_PORT}..."
cd ${COMFYUI_PATH}
python main.py \
    --listen 0.0.0.0 \
    --port ${COMFYUI_PORT} \
    --enable-cors-header \
    --preview-method auto \
    2>&1 | tee /tmp/comfyui.log &

COMFYUI_PID=$!
echo "[INFO] ComfyUI started with PID ${COMFYUI_PID}"

# Wait for ComfyUI to be ready
wait_for_comfyui

# Start Gradio app
echo "[INFO] Starting Gradio app on port ${GRADIO_PORT}..."
cd /app
export COMFYUI_SERVER="127.0.0.1:${COMFYUI_PORT}"
export COMFYUI_INPUT_DIR="${COMFYUI_PATH}/input"
export COMFYUI_OUTPUT_DIR="${COMFYUI_PATH}/output"

python app.py &
GRADIO_PID=$!
echo "[INFO] Gradio started with PID ${GRADIO_PID}"

echo "=========================================="
echo "  Services started successfully!"
echo "  ComfyUI: http://0.0.0.0:${COMFYUI_PORT}"
echo "  Gradio:  http://0.0.0.0:${GRADIO_PORT}"
echo "=========================================="

# Wait for both processes
wait $COMFYUI_PID $GRADIO_PID
