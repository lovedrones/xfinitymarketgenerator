# Dockerfile for HuggingFace Spaces
# This runs both ComfyUI and Gradio app

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install ComfyUI (if not using external server)
# Uncomment if running ComfyUI in the same container
# RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app/ComfyUI

# Copy application files
COPY app.py .
COPY workflow_loader.py .
COPY comfyui_client.py .
COPY model_loader.py .
COPY workflows/ ./workflows/
COPY start_comfyui.sh .

# Expose ports
EXPOSE 7860 8000

# Start both services
CMD ["sh", "-c", "python app.py & python -m uvicorn main:app --host 0.0.0.0 --port 8000"]

