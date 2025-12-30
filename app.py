"""
Gradio App for ComfyUI Product Photography Generator
Hosted on HuggingFace Spaces
"""
import gradio as gr
import os
import sys
import time
import subprocess
import threading
import uuid
from PIL import Image
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_loader import WorkflowLoader
from comfyui_client import ComfyUIClient
from model_loader import ModelLoader

# Configuration from environment
COMFYUI_SERVER = os.getenv("COMFYUI_SERVER", "127.0.0.1:8188")
COMFYUI_INPUT_DIR = os.getenv("COMFYUI_INPUT_DIR", "input")
COMFYUI_OUTPUT_DIR = os.getenv("COMFYUI_OUTPUT_DIR", "output")
GRADIO_PORT = int(os.getenv("GRADIO_PORT", "7860"))

# Initialize components
workflow_loader = WorkflowLoader(workflows_dir="workflows")
model_loader = ModelLoader(cache_dir="models")

# ComfyUI client - will connect when server is available
comfyui_client = None

# Default settings
DEFAULT_NEGATIVE_PROMPT = "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark, text, logo, out of frame, cropped, grainy, noise"

# Example prompts
EXAMPLE_PROMPTS = [
    "A professional e-commerce product photo of the same object. Perfect studio lighting, clean white background, soft shadows, center composition, 85mm camera lens, ultra sharp, realistic, high detail, commercial photography",
    "A lifestyle product photo of the same smartphone on a rustic wooden cafe table next to a steaming latte in a ceramic cup. Warm morning sunlight, cozy coffee shop atmosphere, bokeh background with blurred patrons, Instagram aesthetic, Canon 50mm f/1.4 lens",
    "A premium product photo of the same object placed on elegant white Carrara marble surface with subtle gold veining. Soft natural window light from the left, shallow depth of field, minimalist composition, luxury brand aesthetic, editorial photography style"
]


def check_comfyui_status():
    """Check if ComfyUI is running and return status"""
    global comfyui_client
    
    if comfyui_client is None:
        comfyui_client = ComfyUIClient(server_address=COMFYUI_SERVER)
    
    if comfyui_client.is_server_running():
        return True, "✅ ComfyUI connected"
    else:
        return False, "⏳ Waiting for ComfyUI..."


def initialize_comfyui():
    """Initialize ComfyUI client connection with retry"""
    global comfyui_client
    
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        is_running, status = check_comfyui_status()
        if is_running:
            return status
        time.sleep(retry_delay)
    
    return "⚠️ ComfyUI server not responding. Please check logs."


def ensure_models(workflow_type: str):
    """Ensure required models are downloaded"""
    if workflow_type == "basic":
        model_keys = [
            "juggernautXL_v9",
            "ip-adapter-plus_sdxl_vit-h",
            "CLIP-ViT-H-14-laion2B-s32B-b79K"
        ]
    else:  # advanced
        model_keys = [
            "juggernautXL_v9",
            "ip-adapter-plus_sdxl_vit-h",
            "CLIP-ViT-H-14-laion2B-s32B-b79K",
            "controlnet-canny-sdxl"
        ]
    
    try:
        model_loader.ensure_models(model_keys)
        return "✅ Models ready"
    except Exception as e:
        return f"⚠️ Model loading: {str(e)}"


def generate_image(
    image: Image.Image,
    prompt: str,
    workflow_type: str,
    ipadapter_weight: float,
    controlnet_strength: float,
    cfg_scale: float,
    steps: int,
    resolution: str,
    progress=gr.Progress()
) -> tuple:
    """
    Generate product photography image
    
    Args:
        image: Input product image
        prompt: Generation prompt
        workflow_type: "basic" or "advanced"
        ipadapter_weight: IP-Adapter strength (0.0-1.0)
        controlnet_strength: ControlNet strength (0.0-1.0)
        cfg_scale: CFG scale
        steps: Number of sampling steps
        resolution: Resolution string (e.g., "1024x1024")
        progress: Gradio progress tracker
        
    Returns:
        Tuple of (generated_image, status_message)
    """
    global comfyui_client
    
    try:
        if image is None:
            return None, "❌ Please upload a product image first."
        
        progress(0.05, desc="Checking connection...")
        
        # Check ComfyUI connection
        is_running, status = check_comfyui_status()
        if not is_running:
            return None, "❌ ComfyUI server is not running. Please wait for startup."
        
        progress(0.1, desc="Loading workflow...")
        
        # Load workflow
        workflow_file = "basic.json" if workflow_type == "basic" else "advanced.json"
        workflow = workflow_loader.load_workflow(workflow_file)
        
        if workflow is None:
            return None, f"❌ Could not load workflow: {workflow_file}"
        
        progress(0.2, desc="Checking models...")
        
        # Check models (non-blocking - they should be pre-downloaded)
        model_status = ensure_models(workflow_type)
        
        progress(0.3, desc="Processing image...")
        
        # Save uploaded image to ComfyUI input directory
        os.makedirs(COMFYUI_INPUT_DIR, exist_ok=True)
        
        # Generate unique filename
        image_filename = f"product_{uuid.uuid4().hex[:8]}.png"
        image_path = os.path.join(COMFYUI_INPUT_DIR, image_filename)
        
        # Ensure image is in RGB mode
        if image.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        image.save(image_path, 'PNG')
        
        progress(0.4, desc="Configuring workflow...")
        
        # Update workflow with user inputs
        workflow = workflow_loader.update_image(workflow, image_filename)
        workflow = workflow_loader.update_prompt(workflow, prompt, DEFAULT_NEGATIVE_PROMPT)
        
        # Parse resolution
        width, height = map(int, resolution.split('x'))
        
        # Update settings
        update_kwargs = {
            "ipadapter_weight": ipadapter_weight,
            "cfg_scale": cfg_scale,
            "steps": steps,
            "resolution": (width, height)
        }
        
        if workflow_type == "advanced":
            update_kwargs["controlnet_strength"] = controlnet_strength
        
        workflow = workflow_loader.update_settings(workflow, **update_kwargs)
        
        progress(0.5, desc="Preparing generation...")
        
        # Convert to API format
        api_workflow = workflow_loader.workflow_to_api_format(workflow)
        
        progress(0.6, desc="Generating image...")
        
        # Generate image with progress updates
        def progress_callback(value, message):
            progress(0.6 + value * 0.35, desc=message)
        
        generated_image = comfyui_client.generate_image(
            api_workflow,
            prompt,
            DEFAULT_NEGATIVE_PROMPT,
            progress_callback=progress_callback
        )
        
        progress(0.95, desc="Finalizing...")
        
        # Cleanup input image
        try:
            if os.path.exists(image_path):
                os.unlink(image_path)
        except:
            pass
        
        progress(1.0, desc="Complete!")
        
        if generated_image:
            return generated_image, "✅ Image generated successfully!"
        else:
            return None, "❌ Generation failed. Check ComfyUI logs for details."
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Generation error: {error_details}")
        return None, f"❌ Error: {str(e)}"


def get_status():
    """Get current system status"""
    is_running, comfyui_status = check_comfyui_status()
    
    status_lines = [
        f"**ComfyUI**: {comfyui_status}",
        f"**Server**: {COMFYUI_SERVER}",
    ]
    
    return "\n".join(status_lines)


# Custom CSS for better appearance
custom_css = """
.gradio-container {
    max-width: 1200px !important;
}
.status-box {
    padding: 10px;
    border-radius: 8px;
    background: #f0f0f0;
}
"""

# Create Gradio interface
with gr.Blocks(
    title="Product Photography Generator",
    theme=gr.themes.Soft(),
    css=custom_css
) as app:
    gr.Markdown("""
    # 🎨 Product Photography Generator
    
    Generate professional product photos with AI. Upload your product image, enter a prompt, and get stunning results!
    
    **Features:**
    - ✨ Automatic background handling
    - 🔒 Product identity preservation (IP-Adapter)
    - 📐 Layout control (ControlNet - Advanced mode)
    - 🎯 Multiple style options
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Input")
            
            input_image = gr.Image(
                label="Upload Product Image",
                type="pil",
                height=300,
                sources=["upload", "clipboard"]
            )
            
            prompt = gr.Textbox(
                label="Prompt",
                placeholder="Describe the scene you want...",
                lines=3,
                value=EXAMPLE_PROMPTS[0]
            )
            
            with gr.Row():
                workflow_type = gr.Radio(
                    choices=[
                        ("Basic (Faster)", "basic"),
                        ("Advanced (ControlNet)", "advanced")
                    ],
                    value="basic",
                    label="Workflow"
                )
            
            with gr.Accordion("⚙️ Advanced Settings", open=False):
                ipadapter_weight = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.9,
                    step=0.05,
                    label="IP-Adapter Strength",
                    info="Higher = more identity preservation"
                )
                
                controlnet_strength = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.35,
                    step=0.05,
                    label="ControlNet Strength",
                    info="Advanced workflow only"
                )
                
                cfg_scale = gr.Slider(
                    minimum=1.0,
                    maximum=20.0,
                    value=7.5,
                    step=0.5,
                    label="CFG Scale",
                    info="Prompt adherence"
                )
                
                steps = gr.Slider(
                    minimum=10,
                    maximum=50,
                    value=30,
                    step=5,
                    label="Steps",
                    info="More = better quality but slower"
                )
                
                resolution = gr.Dropdown(
                    choices=["1024x1024", "768x768", "512x512"],
                    value="1024x1024",
                    label="Resolution"
                )
            
            generate_btn = gr.Button(
                "🚀 Generate",
                variant="primary",
                size="lg"
            )
            
            status_text = gr.Textbox(
                label="Status",
                interactive=False,
                value="Initializing...",
                lines=2
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 🖼️ Output")
            
            output_image = gr.Image(
                label="Generated Image",
                type="pil",
                height=500,
                show_download_button=True
            )
            
            gr.Markdown("### 💡 Example Prompts")
            gr.Examples(
                examples=[
                    [EXAMPLE_PROMPTS[0]],
                    [EXAMPLE_PROMPTS[1]],
                    [EXAMPLE_PROMPTS[2]]
                ],
                inputs=prompt,
                label=""
            )
    
    gr.Markdown("""
    ---
    **Tips:**
    - Use **Basic** mode for faster generation with strong product identity
    - Use **Advanced** mode for more control over layout and composition
    - Higher IP-Adapter weight = product looks more like the original
    - Adjust CFG scale if the result doesn't match your prompt
    """)
    
    # Event handlers
    generate_btn.click(
        fn=generate_image,
        inputs=[
            input_image,
            prompt,
            workflow_type,
            ipadapter_weight,
            controlnet_strength,
            cfg_scale,
            steps,
            resolution
        ],
        outputs=[output_image, status_text]
    )
    
    # Initialize on load
    app.load(
        fn=initialize_comfyui,
        outputs=status_text
    )


if __name__ == "__main__":
    print(f"Starting Gradio app on port {GRADIO_PORT}...")
    print(f"ComfyUI server: {COMFYUI_SERVER}")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=GRADIO_PORT,
        share=False,
        show_error=True
    )
