"""
ComfyUI API Client - Communicate with ComfyUI backend
"""
import json
import time
import requests
import uuid
from typing import Dict, Any, Optional, Tuple
import io
from PIL import Image


class ComfyUIClient:
    """Client for interacting with ComfyUI API"""
    
    def __init__(self, server_address: str = "127.0.0.1:8000"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        
    def _get_url(self, endpoint: str) -> str:
        """Get full URL for API endpoint"""
        return f"http://{self.server_address}/{endpoint}"
    
    def queue_prompt(self, prompt: Dict[str, Any]) -> str:
        """
        Queue a prompt for execution
        
        Args:
            prompt: Workflow in API format
            
        Returns:
            Prompt ID
        """
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        
        response = requests.post(
            self._get_url("prompt"),
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            error = response.json()
            raise Exception(f"Error queueing prompt: {error}")
        
        result = response.json()
        return result['prompt_id']
    
    def get_history(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution history for a prompt
        
        Args:
            prompt_id: Prompt ID from queue_prompt
            
        Returns:
            History entry or None
        """
        response = requests.get(self._get_url("history/" + prompt_id))
        
        if response.status_code == 200:
            history = response.json()
            return history.get(prompt_id)
        return None
    
    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> Image.Image:
        """
        Download an image from ComfyUI
        
        Args:
            filename: Image filename
            subfolder: Subfolder path
            folder_type: Type of folder (output, input, temp)
            
        Returns:
            PIL Image object
        """
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = "&".join([f"{k}={v}" for k, v in data.items()])
        
        response = requests.get(self._get_url(f"view?{url_values}"))
        
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            raise Exception(f"Error downloading image: {response.status_code}")
    
    def wait_for_completion(self, prompt_id: str, timeout: int = 300, check_interval: float = 1.0, progress_callback=None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Wait for a prompt to complete
        
        Args:
            prompt_id: Prompt ID
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            progress_callback: Optional callback function(progress, message)
            
        Returns:
            Tuple of (success, history_entry)
        """
        start_time = time.time()
        last_progress = 0
        
        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)
            
            if history:
                # Check if completed
                if len(history.get('outputs', {})) > 0:
                    if progress_callback:
                        progress_callback(1.0, "Complete!")
                    return True, history
                    
                # Check if there was an error
                if 'status' in history and history['status'].get('completed', False):
                    if history['status'].get('success', True):
                        return True, history
                    else:
                        return False, history
                
                # Update progress based on time elapsed
                elapsed = time.time() - start_time
                estimated_progress = min(0.9, elapsed / 60)  # Assume ~60s for generation
                
                if progress_callback and estimated_progress > last_progress:
                    last_progress = estimated_progress
                    progress_callback(estimated_progress, f"Generating... ({int(elapsed)}s)")
            
            time.sleep(check_interval)
        
        return False, None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        try:
            response = requests.get(self._get_url("queue"), timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {"queue_running": [], "queue_pending": []}
    
    def generate_image(self, workflow: Dict[str, Any], 
                      prompt: str,
                      negative_prompt: str = "",
                      progress_callback=None,
                      **kwargs) -> Image.Image:
        """
        Generate an image from a workflow
        
        Args:
            workflow: Workflow dictionary (API format)
            prompt: Positive prompt
            negative_prompt: Negative prompt
            progress_callback: Optional callback function(progress, message)
            **kwargs: Additional settings
            
        Returns:
            Generated PIL Image
        """
        # Queue the prompt
        prompt_id = self.queue_prompt(workflow)
        
        if progress_callback:
            progress_callback(0.1, "Queued for generation...")
        
        # Wait for completion with progress updates
        success, history = self.wait_for_completion(
            prompt_id,
            progress_callback=progress_callback
        )
        
        if not success:
            raise Exception(f"Generation failed: {history}")
        
        if progress_callback:
            progress_callback(0.95, "Downloading result...")
        
        # Get the output image
        outputs = history.get('outputs', {})
        if not outputs:
            raise Exception("No outputs in history")
        
        # Find the SaveImage node output
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                image_info = node_output['images'][0]
                filename = image_info['filename']
                subfolder = image_info.get('subfolder', '')
                
                return self.get_image(filename, subfolder)
        
        raise Exception("No image found in outputs")
    
    def is_server_running(self) -> bool:
        """Check if ComfyUI server is running"""
        try:
            response = requests.get(self._get_url(""), timeout=5)
            return response.status_code == 200
        except:
            return False

