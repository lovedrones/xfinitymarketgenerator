# ComfyUI Product Photography Generator

AI-powered product photography generation using ComfyUI with IP-Adapter and ControlNet for identity preservation and layout control.

## Features

- **Automatic Background Removal** - Images are automatically processed to remove backgrounds
- **Product Identity Preservation** - IP-Adapter maintains product identity across different scenes
- **Layout Control** - ControlNet for precise positioning and edge control
- **Two Workflows** - Basic and advanced options for different use cases

## Setup

### Models Required

- **Base Model:** Juggernaut XL v9 (6.6GB)
- **IP-Adapter Plus SDXL** (808MB)
- **IP-Adapter SDXL** (670MB)
- **CLIP Vision ViT-H-14** (2.4GB)
- **ControlNet Canny SDXL** (2.3GB)
- **ControlNet Depth SDXL** (4.7GB)

### Custom Nodes Installed

- ComfyUI-Manager
- ComfyUI_IPAdapter_plus
- comfyui_controlnet_aux
- was-node-suite-comfyui (for background removal)

## Workflows

### Workflow 1: Basic IP-Adapter
**File:** `user/default/workflows/product_photography_ipadapter.json`

- IP-Adapter weight: 0.9 (strong identity preservation)
- Resolution: 1024x1024
- Automatic background removal
- Best for: Quick product shots with identity preservation

### Workflow 2: IP-Adapter + ControlNet
**File:** `user/default/workflows/product_photography_ipadapter_controlnet.json`

- IP-Adapter weight: 0.55 (balanced prompt following)
- ControlNet strength: 0.35
- Resolution: 768x768 (memory optimized)
- Steps: 25
- Automatic background removal
- Best for: Lifestyle shots with layout control

## Usage

1. Load a workflow in ComfyUI
2. Upload your product image (background will be removed automatically)
3. Enter your prompt
4. Click "Queue Prompt" to generate

## Example Prompts

See `user/default/workflows/README_PRODUCT_PHOTOGRAPHY.md` for detailed prompt examples and settings.

## License

This project uses ComfyUI and various open-source models. Please refer to individual model licenses.

