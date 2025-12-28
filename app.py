"""
Gradio App for ComfyUI Product Photography Generator
Hosted on HuggingFace Spaces
"""
import gradio as gr
import os
import tempfile
import uuid
from PIL import Image
import json
from workflow_loader import WorkflowLoader
from comfyui_client import ComfyUIClient
from model_loader import ModelLoader

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


def initialize_comfyui():
    """Initialize ComfyUI client connection"""
    global comfyui_client
    
    # Try to connect to ComfyUI
    # On HuggingFace Spaces, ComfyUI might run on a different port or need to be started
    server_address = os.getenv("COMFYUI_SERVER", "127.0.0.1:8000")
    comfyui_client = ComfyUIClient(server_address=server_address)
    
    if comfyui_client.is_server_running():
        return "✅ Connected to ComfyUI"
    else:
        return "⚠️ ComfyUI server not running. Please ensure ComfyUI is started."


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
        return f"❌ Error loading models: {str(e)}"


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
    try:
        progress(0.1, desc="Initializing...")
        
        # Check ComfyUI connection
        if not comfyui_client or not comfyui_client.is_server_running():
            return None, "❌ ComfyUI server is not running. Please start ComfyUI first."
        
        progress(0.2, desc="Loading workflow...")
        
        # Load workflow
        workflow_file = "basic.json" if workflow_type == "basic" else "advanced.json"
        workflow = workflow_loader.load_workflow(workflow_file)
        
        progress(0.3, desc="Ensuring models are available...")
        
        # Ensure models are downloaded
        model_status = ensure_models(workflow_type)
        if "❌" in model_status:
            return None, model_status
        
        progress(0.4, desc="Processing image...")
        
        # Save uploaded image to ComfyUI input directory
        input_dir = os.getenv("COMFYUI_INPUT_DIR", "input")
        os.makedirs(input_dir, exist_ok=True)
        
        # Generate unique filename
        image_filename = f"product_{uuid.uuid4().hex[:8]}.png"
        image_path = os.path.join(input_dir, image_filename)
        image.save(image_path)
        
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
        
        progress(0.5, desc="Converting workflow to API format...")
        
        # Convert to API format
        api_workflow = workflow_loader.workflow_to_api_format(workflow)
        
        progress(0.6, desc="Queueing generation...")
        
        # Generate image
        generated_image = comfyui_client.generate_image(
            api_workflow,
            prompt,
            DEFAULT_NEGATIVE_PROMPT
        )
        
        progress(1.0, desc="Complete!")
        
        # Cleanup input image (optional - keep for debugging)
        try:
            if os.path.exists(image_path):
                os.unlink(image_path)
        except:
            pass
        
        return generated_image, "✅ Image generated successfully!"
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Product Photography Generator", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🎨 Product Photography Generator
    
    Generate professional product photos with AI. Upload your product image, enter a prompt, and get stunning results!
    
    **Features:**
    - ✨ Automatic background removal
    - 🔒 Product identity preservation
    - 🎯 Multiple style options
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Input")
            
            input_image = gr.Image(
                label="Upload Product Image",
                type="pil",
                height=300
            )
            
            prompt = gr.Textbox(
                label="Prompt",
                placeholder="A professional e-commerce product photo of the same object...",
                lines=3,
                value=EXAMPLE_PROMPTS[0]
            )
            
            workflow_type = gr.Radio(
                choices=[("Basic (IP-Adapter Only)", "basic"), ("Advanced (IP-Adapter + ControlNet)", "advanced")],
                value="basic",
                label="Workflow Type"
            )
            
            gr.Markdown("### ⚙️ Settings")
            
            ipadapter_weight = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.9,
                step=0.05,
                label="IP-Adapter Strength (higher = more identity preservation)"
            )
            
            controlnet_strength = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.35,
                step=0.05,
                label="ControlNet Strength (advanced workflow only)"
            )
            
            cfg_scale = gr.Slider(
                minimum=1.0,
                maximum=20.0,
                value=7.5,
                step=0.5,
                label="CFG Scale"
            )
            
            steps = gr.Slider(
                minimum=10,
                maximum=50,
                value=30,
                step=5,
                label="Sampling Steps"
            )
            
            resolution = gr.Dropdown(
                choices=["1024x1024", "768x768", "512x512"],
                value="1024x1024",
                label="Resolution"
            )
            
            generate_btn = gr.Button("Generate", variant="primary", size="lg")
            
            status_text = gr.Textbox(
                label="Status",
                interactive=False,
                value="Ready to generate"
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 🖼️ Output")
            
            output_image = gr.Image(
                label="Generated Image",
                type="pil",
                height=500
            )
            
            gr.Examples(
                examples=[[EXAMPLE_PROMPTS[0]], [EXAMPLE_PROMPTS[1]], [EXAMPLE_PROMPTS[2]]],
                inputs=prompt,
                label="Example Prompts"
            )
    
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
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)

