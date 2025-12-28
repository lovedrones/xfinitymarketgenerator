"""
Model Loader - Download and manage models from HuggingFace
"""
import os
from huggingface_hub import hf_hub_download, snapshot_download
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelLoader:
    """Load models from HuggingFace Hub"""
    
    def __init__(self, cache_dir: str = "models"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Model mappings - HuggingFace repo IDs
        self.model_mappings = {
            "juggernautXL_v9": {
                "repo_id": "RunDiffusion/Juggernaut-XL-v9",
                "filename": "Juggernaut-XL-v9.safetensors",
                "subfolder": None,
                "local_dir": "checkpoints"
            },
            "ip-adapter-plus_sdxl_vit-h": {
                "repo_id": "h94/IP-Adapter",
                "filename": "ip-adapter-plus_sdxl_vit-h.safetensors",
                "subfolder": "sdxl_models",
                "local_dir": "ipadapter"
            },
            "ip-adapter_sdxl": {
                "repo_id": "h94/IP-Adapter",
                "filename": "ip-adapter_sdxl.safetensors",
                "subfolder": "sdxl_models",
                "local_dir": "ipadapter"
            },
            "CLIP-ViT-H-14-laion2B-s32B-b79K": {
                "repo_id": "h94/IP-Adapter",
                "filename": "model.safetensors",
                "subfolder": "models/image_encoder",
                "local_dir": "clip_vision"
            },
            "controlnet-canny-sdxl": {
                "repo_id": "xinsir/controlnet-canny-sdxl-1.0",
                "filename": "diffusion_pytorch_model.safetensors",
                "subfolder": None,
                "local_dir": "controlnet"
            },
            "controlnet-depth-sdxl": {
                "repo_id": "diffusers/controlnet-depth-sdxl-1.0",
                "filename": "diffusion_pytorch_model.safetensors",
                "subfolder": None,
                "local_dir": "controlnet"
            }
        }
    
    def download_model(self, model_key: str, force_download: bool = False) -> str:
        """
        Download a model from HuggingFace
        
        Args:
            model_key: Key from model_mappings
            force_download: Force re-download even if exists
            
        Returns:
            Local path to downloaded model
        """
        if model_key not in self.model_mappings:
            raise ValueError(f"Unknown model: {model_key}")
        
        model_info = self.model_mappings[model_key]
        local_dir = os.path.join(self.cache_dir, model_info["local_dir"])
        os.makedirs(local_dir, exist_ok=True)
        
        local_path = os.path.join(local_dir, model_info["filename"])
        
        # Check if already exists
        if os.path.exists(local_path) and not force_download:
            logger.info(f"Model already exists: {local_path}")
            return local_path
        
        logger.info(f"Downloading {model_key} from HuggingFace...")
        
        try:
            downloaded_path = hf_hub_download(
                repo_id=model_info["repo_id"],
                filename=model_info["filename"],
                subfolder=model_info.get("subfolder"),
                cache_dir=self.cache_dir,
                local_dir=local_dir,
                force_download=force_download
            )
            
            logger.info(f"Downloaded {model_key} to {downloaded_path}")
            return downloaded_path
            
        except Exception as e:
            logger.error(f"Error downloading {model_key}: {e}")
            raise
    
    def ensure_models(self, model_keys: list, force_download: bool = False) -> Dict[str, str]:
        """
        Ensure multiple models are downloaded
        
        Args:
            model_keys: List of model keys to download
            force_download: Force re-download
            
        Returns:
            Dictionary mapping model keys to local paths
        """
        paths = {}
        for key in model_keys:
            try:
                paths[key] = self.download_model(key, force_download)
            except Exception as e:
                logger.error(f"Failed to download {key}: {e}")
                raise
        
        return paths
    
    def get_model_path(self, model_key: str) -> Optional[str]:
        """
        Get local path to a model if it exists
        
        Args:
            model_key: Model key
            
        Returns:
            Local path or None if not found
        """
        if model_key not in self.model_mappings:
            return None
        
        model_info = self.model_mappings[model_key]
        local_path = os.path.join(
            self.cache_dir,
            model_info["local_dir"],
            model_info["filename"]
        )
        
        if os.path.exists(local_path):
            return local_path
        
        return None

