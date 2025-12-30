# 🚀 Deployment Guide - HuggingFace Spaces

This guide explains how to deploy the Product Photography Generator to HuggingFace Spaces with full ComfyUI integration.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   HuggingFace Spaces                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Docker Container                      ││
│  │  ┌───────────────┐        ┌───────────────────────────┐ ││
│  │  │   Gradio App  │◄──────►│     ComfyUI Backend       │ ││
│  │  │   Port 7860   │  API   │       Port 8188           │ ││
│  │  └───────────────┘        └───────────────────────────┘ ││
│  │                                     │                    ││
│  │                           ┌─────────▼─────────┐          ││
│  │                           │      Models       │          ││
│  │                           │ (Downloaded from  │          ││
│  │                           │  HuggingFace Hub) │          ││
│  │                           └───────────────────┘          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Quick Deploy

### Step 1: Create HuggingFace Space

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Configure:
   - **Name**: `product-photography-generator`
   - **SDK**: Docker
   - **Hardware**: GPU T4 (or better)
   - **Visibility**: Public or Private

### Step 2: Connect GitHub Repository

1. In your Space settings, go to "Files and versions"
2. Choose "Link to GitHub repository"
3. Connect: `lovedrones/xfinitymarketgenerator`
4. Select branch: `main`

### Step 3: Wait for Build

The Space will automatically:
1. Build the Docker image
2. Install ComfyUI and dependencies
3. Clone custom nodes
4. Start both services

First deployment takes ~15-20 minutes due to model downloads.

## Configuration

### Environment Variables

Set these in your Space settings if needed:

| Variable | Default | Description |
|----------|---------|-------------|
| `COMFYUI_PORT` | `8188` | ComfyUI server port |
| `GRADIO_PORT` | `7860` | Gradio web interface port |
| `HF_TOKEN` | - | HuggingFace token (for private models) |

### Hardware Requirements

| Tier | GPU | RAM | Recommended For |
|------|-----|-----|-----------------|
| Free | None | 16GB | Testing only (CPU inference very slow) |
| **T4 Small** | T4 16GB | 16GB | ✅ Recommended minimum |
| T4 Medium | T4 16GB | 32GB | Better for advanced workflow |
| A10G Small | A10G 24GB | 24GB | Faster generation |
| A100 | A100 40GB | 80GB | Production/high volume |

## Files Structure

```
├── Dockerfile              # Docker build configuration
├── start_comfyui.sh        # Startup script (downloads models, starts services)
├── app.py                  # Gradio web interface
├── comfyui_client.py       # ComfyUI API client
├── workflow_loader.py      # Workflow JSON management
├── model_loader.py         # HuggingFace model downloader
├── requirements.txt        # Python dependencies
└── workflows/
    ├── basic.json          # IP-Adapter only workflow
    └── advanced.json       # IP-Adapter + ControlNet workflow
```

## Models (Auto-Downloaded)

The following models are automatically downloaded on first startup:

| Model | Size | Source |
|-------|------|--------|
| Juggernaut XL v9 | ~6.6GB | RunDiffusion/Juggernaut-XL-v9 |
| IP-Adapter Plus SDXL | ~808MB | h94/IP-Adapter |
| CLIP Vision ViT-H-14 | ~2.4GB | h94/IP-Adapter |
| ControlNet Canny SDXL | ~2.3GB | xinsir/controlnet-canny-sdxl-1.0 |

**Total Storage Required**: ~20GB (including ComfyUI + custom nodes)

## Troubleshooting

### Space Won't Start

1. Check build logs for errors
2. Verify hardware tier has enough resources
3. Check if models are downloading properly

### Generation Fails

1. Check ComfyUI is running: Look for "ComfyUI connected" status
2. Verify workflows are valid JSON
3. Check Gradio logs for error details

### Out of Memory

1. Use "Basic" workflow (no ControlNet)
2. Reduce resolution to 768x768 or 512x512
3. Upgrade hardware tier

### Models Not Loading

1. Check HuggingFace Hub connectivity
2. Verify model repository exists
3. Check disk space in container

## Local Development

To run locally:

```bash
# Clone repository
git clone https://github.com/lovedrones/xfinitymarketgenerator.git
cd xfinitymarketgenerator

# Install dependencies
pip install -r requirements.txt

# Start ComfyUI (in separate terminal)
cd /path/to/ComfyUI
python main.py --listen 0.0.0.0 --port 8188

# Start Gradio app
python app.py
```

## API Usage

The Gradio app exposes an API that can be called programmatically:

```python
from gradio_client import Client

client = Client("your-username/product-photography-generator")

result = client.predict(
    image="path/to/product.png",
    prompt="Professional studio photo on white background",
    workflow_type="basic",
    ipadapter_weight=0.9,
    controlnet_strength=0.35,
    cfg_scale=7.5,
    steps=30,
    resolution="1024x1024",
    api_name="/generate_image"
)
```

## Updates

To update your Space:

1. Push changes to GitHub
2. HuggingFace will automatically rebuild
3. Or click "Factory reboot" in Space settings

## Support

- GitHub Issues: [lovedrones/xfinitymarketgenerator](https://github.com/lovedrones/xfinitymarketgenerator/issues)
- HuggingFace Discussions: In your Space's community tab

---

**Made with ❤️ for product photographers and e-commerce creators**
