# 🚀 HuggingFace Spaces Deployment Guide

This guide explains how to deploy the Product Photography Generator to HuggingFace Spaces.

## Quick Start

1. **Fork this repository** to your GitHub account
2. **Create a new Space** on [HuggingFace Spaces](https://huggingface.co/spaces)
3. **Select Gradio SDK**
4. **Connect your GitHub repository**
5. **Deploy!**

## Space Configuration

### Required Files

- `app.py` - Main Gradio application
- `requirements.txt` - Python dependencies
- `workflows/basic.json` - Basic workflow
- `workflows/advanced.json` - Advanced workflow
- `workflow_loader.py` - Workflow management
- `comfyui_client.py` - ComfyUI API client
- `model_loader.py` - HuggingFace model loader

### Environment Variables

Set these in your Space settings:

- `COMFYUI_SERVER` - ComfyUI server address (default: `127.0.0.1:8000`)
- `HF_TOKEN` - HuggingFace token for model downloads (optional, for private models)

### Hardware Requirements

**Recommended:**
- GPU: T4 or better
- RAM: 16GB+
- Disk: 50GB+ (for model caching)

**Minimum:**
- GPU: Any CUDA-compatible
- RAM: 8GB
- Disk: 30GB

## Running ComfyUI Backend

The app requires a ComfyUI backend. You have two options:

### Option 1: Run ComfyUI in the Same Space

Create a `Dockerfile` or use a startup script to run ComfyUI alongside the Gradio app.

### Option 2: Use External ComfyUI Server

Point `COMFYUI_SERVER` to an external ComfyUI instance.

## Model Loading

Models are automatically downloaded from HuggingFace on first use:

- **Juggernaut XL v9** - Base model
- **IP-Adapter Plus SDXL** - Identity preservation
- **CLIP Vision ViT-H-14** - Image encoding
- **ControlNet Canny SDXL** - Layout control (advanced workflow)

Models are cached after first download for faster subsequent runs.

## Usage

1. Upload a product image
2. Enter your prompt
3. Select workflow type (Basic or Advanced)
4. Adjust settings
5. Click "Generate"

## Troubleshooting

### Models Not Downloading

- Check HuggingFace token is set (if using private models)
- Verify internet connection
- Check disk space

### ComfyUI Connection Failed

- Ensure ComfyUI is running
- Check `COMFYUI_SERVER` environment variable
- Verify port is accessible

### Out of Memory

- Use Basic workflow (less memory)
- Reduce resolution to 768x768 or 512x512
- Reduce steps to 20-25

## Customization

### Adding New Models

Edit `model_loader.py` to add new model mappings.

### Modifying Workflows

Edit JSON files in `workflows/` directory.

## Support

For issues, please open an issue on GitHub.

