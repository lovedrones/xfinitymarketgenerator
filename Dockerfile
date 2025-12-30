# Dockerfile for HuggingFace Spaces
# Runs ComfyUI backend + Gradio frontend

FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV COMFYUI_PORT=8188
ENV GRADIO_PORT=7860
ENV HF_HOME=/app/hf_cache
ENV TRANSFORMERS_CACHE=/app/hf_cache
ENV COMFYUI_PATH=/app/ComfyUI

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    wget \
    curl \
    python3.11 \
    python3.11-venv \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git ${COMFYUI_PATH}

# Install ComfyUI dependencies
WORKDIR ${COMFYUI_PATH}
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip install --no-cache-dir -r requirements.txt

# Install custom nodes
WORKDIR ${COMFYUI_PATH}/custom_nodes

# ComfyUI Manager
RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git

# IP-Adapter Plus
RUN git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# ControlNet Auxiliary Preprocessors
RUN git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git \
    && pip install --no-cache-dir -r comfyui_controlnet_aux/requirements.txt

# WAS Node Suite (for background removal)
RUN git clone https://github.com/WASasquatch/was-node-suite-comfyui.git \
    && pip install --no-cache-dir -r was-node-suite-comfyui/requirements.txt

# ComfyUI Essentials
RUN git clone https://github.com/cubiq/ComfyUI_essentials.git \
    && pip install --no-cache-dir -r ComfyUI_essentials/requirements.txt || true

# Go back to app directory
WORKDIR /app

# Copy application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY workflow_loader.py .
COPY comfyui_client.py .
COPY model_loader.py .
COPY workflows/ ./workflows/
COPY start_comfyui.sh .
RUN chmod +x start_comfyui.sh

# Create necessary directories
RUN mkdir -p ${COMFYUI_PATH}/models/checkpoints \
    ${COMFYUI_PATH}/models/clip_vision \
    ${COMFYUI_PATH}/models/ipadapter \
    ${COMFYUI_PATH}/models/controlnet \
    ${COMFYUI_PATH}/input \
    ${COMFYUI_PATH}/output \
    /app/hf_cache

# Create user for HuggingFace Spaces
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user

# Expose ports
EXPOSE ${GRADIO_PORT} ${COMFYUI_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${GRADIO_PORT}/ || exit 1

# Start services
CMD ["./start_comfyui.sh"]
