# 🚀 Deployment Guide

This guide explains how to deploy the Product Photography Generator to HuggingFace Spaces.

## Prerequisites

- GitHub repository with the code
- HuggingFace account
- HuggingFace Space (create at https://huggingface.co/spaces)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository has:
- `app.py` - Main Gradio application
- `requirements.txt` - Python dependencies
- `workflows/` - Workflow JSON files
- All Python modules (`workflow_loader.py`, `comfyui_client.py`, `model_loader.py`)

### 2. Create HuggingFace Space

1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in:
   - **Space name**: `product-photography-generator` (or your choice)
   - **SDK**: `Gradio`
   - **Hardware**: `GPU T4` (recommended) or `CPU` (for testing)
   - **Visibility**: Public or Private

### 3. Connect GitHub Repository

1. In Space settings, go to "Repository"
2. Select "Connect to GitHub"
3. Choose your repository
4. Set branch to `main` (or your default branch)

### 4. Configure Environment

In Space settings, add environment variables if needed:
- `COMFYUI_SERVER`: ComfyUI server address (if using external server)
- `HF_TOKEN`: HuggingFace token (for private models)

### 5. Deploy

The Space will automatically build and deploy when you push to the connected branch.

## Alternative: Standalone Deployment

If you want to run without ComfyUI backend, you can use a simplified version that uses `diffusers` directly.

### Simplified Requirements

Create `requirements_simple.txt`:
```
gradio>=4.0.0
pillow>=10.0.0
diffusers>=0.24.0
transformers>=4.35.0
accelerate>=0.25.0
torch>=2.0.0
torchvision>=0.15.0
controlnet-aux>=0.4.0
```

## Troubleshooting

### Build Fails

- Check `requirements.txt` syntax
- Verify all file paths are correct
- Check Space logs for specific errors

### Models Not Loading

- Verify HuggingFace model IDs in `model_loader.py`
- Check disk space (models are large)
- Ensure `huggingface-hub` is in requirements

### ComfyUI Connection Issues

- If using external ComfyUI, verify `COMFYUI_SERVER` is correct
- Check firewall/network settings
- Consider using the standalone diffusers version

### Out of Memory

- Use smaller resolution (512x512 or 768x768)
- Reduce sampling steps
- Use Basic workflow instead of Advanced

## Monitoring

- Check Space logs in the HuggingFace dashboard
- Monitor GPU/RAM usage
- Review user feedback and errors

## Updates

To update your Space:
1. Push changes to your GitHub repository
2. HuggingFace Spaces will automatically rebuild
3. Or manually trigger rebuild in Space settings

## Support

For issues:
1. Check Space logs
2. Review GitHub issues
3. Open a new issue with logs and error messages

