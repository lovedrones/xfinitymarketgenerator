"""
Workflow Loader - Load and modify ComfyUI workflow JSON files programmatically
"""
import json
import os
from typing import Dict, Any, Optional


class WorkflowLoader:
    """Load and modify ComfyUI workflows"""
    
    def __init__(self, workflows_dir: str = "workflows"):
        self.workflows_dir = workflows_dir
        
    def load_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """
        Load a workflow JSON file
        
        Args:
            workflow_name: Name of workflow file (e.g., 'basic.json' or 'advanced.json')
            
        Returns:
            Dictionary containing workflow data
        """
        workflow_path = os.path.join(self.workflows_dir, workflow_name)
        
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")
        
        with open(workflow_path, 'r') as f:
            return json.load(f)
    
    def update_prompt(self, workflow: Dict[str, Any], prompt: str, negative_prompt: str = "") -> Dict[str, Any]:
        """
        Update the prompt in a workflow
        
        Args:
            workflow: Workflow dictionary
            prompt: Positive prompt text
            negative_prompt: Negative prompt text (optional)
            
        Returns:
            Modified workflow dictionary
        """
        for node in workflow.get('nodes', []):
            # Find CLIPTextEncode nodes
            if node.get('type') == 'CLIPTextEncode':
                # Check if it's positive or negative based on position/order
                # Usually first CLIPTextEncode is positive, second is negative
                if 'widgets_values' in node and len(node['widgets_values']) > 0:
                    # Update based on node ID or order
                    node_id = node.get('id')
                    # Typically node 2 is positive, node 3 is negative
                    if node_id == 2 or (not negative_prompt and node.get('order', 0) < 3):
                        node['widgets_values'][0] = prompt
                    elif node_id == 3 or (negative_prompt and node.get('order', 0) >= 3):
                        if negative_prompt:
                            node['widgets_values'][0] = negative_prompt
        
        return workflow
    
    def update_image(self, workflow: Dict[str, Any], image_path: str) -> Dict[str, Any]:
        """
        Update the image path in LoadImage node
        
        Args:
            workflow: Workflow dictionary
            image_path: Path to image file
            
        Returns:
            Modified workflow dictionary
        """
        for node in workflow.get('nodes', []):
            if node.get('type') == 'LoadImage':
                if 'widgets_values' in node:
                    node['widgets_values'][0] = os.path.basename(image_path)
        
        return workflow
    
    def update_settings(self, workflow: Dict[str, Any], 
                       ipadapter_weight: Optional[float] = None,
                       controlnet_strength: Optional[float] = None,
                       cfg_scale: Optional[float] = None,
                       steps: Optional[int] = None,
                       resolution: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Update workflow settings
        
        Args:
            workflow: Workflow dictionary
            ipadapter_weight: IP-Adapter weight (0.0-1.0)
            controlnet_strength: ControlNet strength (0.0-1.0)
            cfg_scale: CFG scale value
            steps: Number of sampling steps
            resolution: Tuple of (width, height)
            
        Returns:
            Modified workflow dictionary
        """
        for node in workflow.get('nodes', []):
            node_type = node.get('type')
            
            # Update IP-Adapter weight
            if node_type == 'IPAdapterAdvanced' and ipadapter_weight is not None:
                if 'widgets_values' in node and len(node['widgets_values']) > 0:
                    node['widgets_values'][0] = ipadapter_weight
            
            # Update ControlNet strength
            if node_type == 'ControlNetApplyAdvanced' and controlnet_strength is not None:
                if 'widgets_values' in node and len(node['widgets_values']) > 0:
                    node['widgets_values'][0] = controlnet_strength
            
            # Update CFG and steps in KSampler
            if node_type == 'KSampler':
                if 'widgets_values' in node:
                    if steps is not None and len(node['widgets_values']) > 2:
                        node['widgets_values'][2] = steps
                    if cfg_scale is not None and len(node['widgets_values']) > 3:
                        node['widgets_values'][3] = cfg_scale
            
            # Update resolution
            if node_type == 'EmptyLatentImage' and resolution is not None:
                if 'widgets_values' in node and len(node['widgets_values']) >= 2:
                    node['widgets_values'][0] = resolution[0]  # width
                    node['widgets_values'][1] = resolution[1]  # height
        
        return workflow
    
    def workflow_to_api_format(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert workflow JSON to ComfyUI API format
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            API-formatted prompt dictionary
        """
        prompt = {}
        
        # Create a mapping of link_id to source node info
        link_map = {}
        for link in workflow.get('links', []):
            if len(link) >= 5:
                link_id, src_node, src_slot, dst_node, dst_slot = link[:5]
                link_map[link_id] = (src_node, src_slot)
        
        for node in workflow.get('nodes', []):
            node_id = str(node['id'])
            class_type = node.get('type')
            inputs = {}
            
            # Process widget values (direct inputs)
            if 'widgets_values' in node:
                widget_idx = 0
                # Get all inputs that have widgets
                for inp in node.get('inputs', []):
                    if inp.get('name'):
                        input_name = inp['name']
                        # Check if this input has a widget (not a link)
                        if 'link' not in inp or inp.get('link') is None:
                            if widget_idx < len(node['widgets_values']):
                                inputs[input_name] = node['widgets_values'][widget_idx]
                                widget_idx += 1
            
            # Process links (connections between nodes)
            for inp in node.get('inputs', []):
                if 'link' in inp and inp['link'] is not None:
                    link_id = inp['link']
                    if link_id in link_map:
                        src_node, src_slot = link_map[link_id]
                        input_name = inp.get('name')
                        inputs[input_name] = [str(src_node), src_slot]
            
            prompt[node_id] = {
                "class_type": class_type,
                "inputs": inputs
            }
        
        return prompt

