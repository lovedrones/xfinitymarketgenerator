# Product Photography Workflow for ComfyUI

## Setup Complete!

All required models and custom nodes have been installed:

### Models Downloaded

| Model | Location | Size |
|-------|----------|------|
| Juggernaut XL v9 | `models/checkpoints/` | 6.6GB |
| IP-Adapter Plus SDXL | `models/ipadapter/` | 808MB |
| IP-Adapter SDXL | `models/ipadapter/` | 670MB |
| CLIP ViT-H-14 | `models/clip_vision/` | 2.4GB |
| ControlNet Canny SDXL | `models/controlnet/` | 2.3GB |
| ControlNet Depth SDXL | `models/controlnet/` | 4.7GB |

### Custom Nodes Installed

- **ComfyUI-Manager** - For easy node management
- **ComfyUI_IPAdapter_plus** - For identity preservation
- **comfyui_controlnet_aux** - For Canny/Depth preprocessing

---

## Available Workflows

### 1. Basic IP-Adapter Product Photography
**File:** `product_photography_ipadapter.json`

Best for: Quick product shots with identity preservation

### 2. IP-Adapter + ControlNet Product Photography
**File:** `product_photography_ipadapter_controlnet.json`

Best for: Precise layout control using edge detection

---

## How to Run

1. **Start ComfyUI:**
   ```bash
   cd /Users/juanlo/Documents/ComfyUI
   python main.py
   ```

2. **Open in Browser:**
   Navigate to `http://127.0.0.1:8188`

3. **Load Workflow:**
   - Click **Load** (top-right corner)
   - Select one of the workflow JSON files

4. **Upload Your Product Image:**
   - Find the **Load Image** node
   - Click to upload your product photo

5. **Customize Prompt (Optional):**
   Edit the positive prompt for different styles:
   
   **Clean Studio:**
   ```
   A professional e-commerce product photo of the same object. Perfect studio lighting, clean white background, soft shadows, center composition, 85mm camera lens, ultra sharp, realistic, high detail
   ```
   
   **Lifestyle:**
   ```
   A product photo of the same object placed on a marble countertop in a modern kitchen. Soft natural daylight, shallow depth of field, cinematic realism
   ```

6. **Adjust IP-Adapter Strength:**
   - `0.8` = High fidelity to original product
   - `0.5` = More creative variation
   - `1.0` = Maximum identity preservation

7. **Set Resolution:**
   - `1024x1024` - Square (Instagram, general use)
   - `768x1024` - Portrait
   - `1536x1024` - Widescreen

8. **Generate:**
   Click **Queue Prompt** and wait for your image!

---

## Tips for Best Results

1. **Use high-quality reference images** - Clean, well-lit product photos work best
2. **Keep lighting prompts consistent** - Match your prompt lighting to desired output
3. **Use fixed seed for repeatability** - Set seed to a number instead of "random"
4. **Try ControlNet for stable angles** - Use the ControlNet workflow for precise positioning
5. **Experiment with IP-Adapter strength** - Find the sweet spot for your products

---

## Troubleshooting

**Missing nodes error:**
- Restart ComfyUI after installing custom nodes
- Use ComfyUI-Manager to install any missing dependencies

**Out of memory:**
- Reduce resolution to 768x768
- Close other GPU-intensive applications

**Poor identity preservation:**
- Increase IP-Adapter strength to 0.9-1.0
- Use higher quality reference images

