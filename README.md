# 🎨 ComfyUI Product Photography Generator

> AI-powered product photography generation with automatic background removal, identity preservation, and layout control using ComfyUI, IP-Adapter, and ControlNet.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-0.6.0-green.svg)](https://github.com/comfyanonymous/ComfyUI)

## ✨ Features

- 🎯 **Automatic Background Removal** - Images are automatically processed to remove backgrounds before generation
- 🔒 **Product Identity Preservation** - IP-Adapter maintains product identity across different scenes and backgrounds
- 📐 **Layout Control** - ControlNet for precise positioning and edge-based layout control
- 🚀 **Two Optimized Workflows** - Basic and advanced options for different use cases
- 💾 **Memory Optimized** - Workflow 2 optimized for systems with limited VRAM
- 🎨 **Multiple Style Support** - Generate product photos in various styles (studio, lifestyle, luxury, etc.)

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Workflows](#-workflows)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🔧 Prerequisites

- **ComfyUI** installed and running
- **Python 3.12+**
- **macOS** (tested on macOS Sequoia)
- **~16.5GB** free disk space for models
- **GPU/Apple Silicon** recommended for faster generation

## 📦 Installation

### 1. Clone This Repository

```bash
git clone https://github.com/lovedrones/xfinitymarketgenerator.git
cd xfinitymarketgenerator
```

### 2. Install Required Models

Download the following models to your ComfyUI installation:

#### Base Model
- **Juggernaut XL v9** (6.6GB)
  - Source: [CivitAI](https://civitai.com/models/133005/juggernaut-xl)
  - Location: `ComfyUI/models/checkpoints/`

#### IP-Adapter Models
- **IP-Adapter Plus SDXL** (808MB)
- **IP-Adapter SDXL** (670MB)
  - Source: [HuggingFace](https://huggingface.co/h94/IP-Adapter-FaceID/tree/main/sdxl_models)
  - Location: `ComfyUI/models/ipadapter/`

#### CLIP Vision
- **CLIP ViT-H-14** (2.4GB)
  - Source: [HuggingFace](https://huggingface.co/h94/IP-Adapter/tree/main/models/image_encoder)
  - Location: `ComfyUI/models/clip_vision/`

#### ControlNet Models (Optional - for Workflow 2)
- **ControlNet Canny SDXL** (2.3GB)
- **ControlNet Depth SDXL** (4.7GB)
  - Source: [HuggingFace](https://huggingface.co/xinsir/controlnet-canny-sdxl-1.0)
  - Location: `ComfyUI/models/controlnet/`

### 3. Install Custom Nodes

The following custom nodes are required:

```bash
cd ComfyUI/custom_nodes

# ComfyUI Manager (for easy node management)
git clone https://github.com/ltdrdata/ComfyUI-Manager.git

# IP-Adapter Plus
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# ControlNet Auxiliary Preprocessors
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git

# WAS Node Suite (for background removal)
git clone https://github.com/WASasquatch/was-node-suite-comfyui.git
```

### 4. Install Python Dependencies

```bash
# Install rembg for background removal
pip install rembg[new]

# Install opencv for ControlNet preprocessing
pip install opencv-python-headless
```

## 🚀 Quick Start

1. **Start ComfyUI**
   ```bash
   # If using desktop app
   open /Applications/ComfyUI.app
   
   # Or if using command line
   cd ComfyUI
   python main.py
   ```

2. **Load a Workflow**
   - Open ComfyUI in your browser: `http://127.0.0.1:8000`
   - Click **Load** (top-right)
   - Navigate to: `user/default/workflows/`
   - Select one of the workflow JSON files

3. **Upload Your Product Image**
   - Find the **Load Image** node
   - Upload your product photo
   - Background will be removed automatically

4. **Generate**
   - Enter your prompt (optional)
   - Click **Queue Prompt**

## 📊 Workflows

### Workflow 1: Basic IP-Adapter
**File:** `user/default/workflows/product_photography_ipadapter.json`

**Best for:** Quick product shots with strong identity preservation

**Settings:**
- IP-Adapter Weight: `0.9` (strong identity preservation)
- Resolution: `1024x1024`
- Steps: `30`
- CFG Scale: `7.5`

**Features:**
- Automatic background removal
- High product identity preservation
- Fast generation

### Workflow 2: IP-Adapter + ControlNet
**File:** `user/default/workflows/product_photography_ipadapter_controlnet.json`

**Best for:** Lifestyle shots with layout control

**Settings:**
- IP-Adapter Weight: `0.55` (balanced prompt following)
- ControlNet Strength: `0.35`
- Resolution: `768x768` (memory optimized)
- Steps: `25`
- CFG Scale: `8.5`

**Features:**
- Automatic background removal
- Edge-based layout control
- Memory optimized for lower VRAM systems
- Better prompt adherence

## 💡 Usage Examples

### Example 1: Clean E-Commerce Studio
```
A professional e-commerce product photo of the same object on a pure white seamless backdrop. Perfect three-point studio lighting, soft diffused shadows, center composition, 85mm lens, f/8 aperture, ultra sharp focus, commercial photography, 8K resolution
```

**Recommended Settings:**
- Workflow: 1
- IP-Adapter: 0.85-0.9
- CFG: 7.5

### Example 2: Coffee Shop Lifestyle
```
A lifestyle product photo of the same smartphone on a rustic wooden cafe table next to a steaming latte in a ceramic cup. Warm morning sunlight, cozy coffee shop atmosphere, bokeh background with blurred patrons, Instagram aesthetic, Canon 50mm f/1.4 lens
```

**Recommended Settings:**
- Workflow: 2
- IP-Adapter: 0.55
- ControlNet: 0.35
- CFG: 8.5

### Example 3: Luxury Marble Surface
```
A premium product photo of the same object placed on elegant white Carrara marble surface with subtle gold veining. Soft natural window light from the left, shallow depth of field, minimalist composition, luxury brand aesthetic, editorial photography style
```

**Recommended Settings:**
- Workflow: 1 or 2
- IP-Adapter: 0.8
- CFG: 7.0

See [`user/default/workflows/README_PRODUCT_PHOTOGRAPHY.md`](user/default/workflows/README_PRODUCT_PHOTOGRAPHY.md) for more examples and detailed settings.

## ⚙️ Configuration

### Adjusting IP-Adapter Strength

| Strength | Use Case |
|----------|----------|
| `0.9-1.0` | Maximum identity preservation, minimal background variation |
| `0.7-0.8` | Strong identity, some background flexibility |
| `0.5-0.6` | Balanced identity and prompt following |
| `0.3-0.4` | More creative variation, less strict identity |

### Adjusting ControlNet Strength

| Strength | Use Case |
|----------|----------|
| `0.6-0.8` | Strict layout control, precise positioning |
| `0.4-0.5` | Moderate layout control |
| `0.2-0.3` | Subtle layout influence |

### Resolution Settings

| Resolution | Memory Usage | Use Case |
|------------|--------------|----------|
| `1024x1024` | High | Best quality, requires more VRAM |
| `768x768` | Medium | Balanced quality and memory |
| `512x512` | Low | Fast generation, lower quality |

## 🐛 Troubleshooting

### Background Removal Not Working

**Issue:** Node shows error or doesn't process images

**Solutions:**
1. Restart ComfyUI after installing custom nodes
2. Verify `rembg` is installed: `pip install rembg[new]`
3. Check node type is `"Image Remove Background (Alpha)"` (not `"WAS_Remove_Background"`)

### Out of Memory Errors

**Issue:** Workflow 2 fails with memory errors

**Solutions:**
1. Use Workflow 2 (already optimized to 768x768)
2. Reduce steps from 25 to 20
3. Close other GPU-intensive applications
4. Use Workflow 1 instead (no ControlNet overhead)

### Product Identity Not Preserved

**Issue:** Generated images don't match the product

**Solutions:**
1. Increase IP-Adapter weight to 0.9-1.0
2. Use higher quality reference images
3. Ensure background is removed before processing
4. Use Workflow 1 for stronger identity preservation

### Node Not Found Errors

**Issue:** "Cannot execute because a node is missing the class_type property"

**Solutions:**
1. Restart ComfyUI completely
2. Verify custom nodes are installed in `custom_nodes/` directory
3. Check ComfyUI logs for import errors
4. Reinstall missing custom nodes via ComfyUI-Manager

## 📁 Project Structure

```
xfinitymarketgenerator/
├── README.md                                    # This file
├── .gitignore                                   # Git ignore rules
├── LICENSE                                      # MIT License
└── user/
    └── default/
        └── workflows/
            ├── product_photography_ipadapter.json              # Workflow 1
            ├── product_photography_ipadapter_controlnet.json   # Workflow 2
            ├── README_PRODUCT_PHOTOGRAPHY.md                   # Detailed guide
            └── queue_workflow.py                               # Helper script
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - The amazing node-based UI
- [IP-Adapter](https://github.com/tencent-research/IP-Adapter) - Identity preservation technology
- [ControlNet](https://github.com/lllyasviel/ControlNet) - Layout control
- [WAS Node Suite](https://github.com/WASasquatch/was-node-suite-comfyui) - Background removal
- Model creators: Juggernaut XL, RealVisXL, and all the amazing model developers

## 📧 Contact

For questions, issues, or suggestions, please open an issue on [GitHub](https://github.com/lovedrones/xfinitymarketgenerator/issues).

---

**Made with ❤️ for product photographers and e-commerce creators**
