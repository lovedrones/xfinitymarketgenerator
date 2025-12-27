#!/usr/bin/env python3
import json
import requests
import sys

# Read the workflow
with open('product_photography_ipadapter_controlnet.json', 'r') as f:
    workflow = json.load(f)

# Build the prompt dictionary
prompt = {}

for node in workflow['nodes']:
    node_id = str(node['id'])
    class_type = node['type']
    inputs = {}
    
    # Process widget values based on node inputs
    if 'inputs' in node and 'widgets_values' in node:
        widget_idx = 0
        for inp in node['inputs']:
            if 'widget' in inp:
                widget_name = inp['widget'].get('name', inp.get('name'))
                if widget_idx < len(node['widgets_values']):
                    inputs[widget_name] = node['widgets_values'][widget_idx]
                    widget_idx += 1
    
    # Process links
    for link in workflow['links']:
        link_id, src_node, src_slot, dst_node, dst_slot, data_type = link
        if dst_node == node['id']:
            # Find which input this link connects to
            for inp in node.get('inputs', []):
                if inp.get('link') == link_id:
                    input_name = inp.get('name')
                    inputs[input_name] = [str(src_node), src_slot]
                    break
    
    prompt[node_id] = {
        "class_type": class_type,
        "inputs": inputs
    }

# Queue the prompt
try:
    response = requests.post('http://127.0.0.1:8000/prompt', json={"prompt": prompt})
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Workflow queued successfully!")
        print(f"   Prompt ID: {result.get('prompt_id', 'N/A')}")
        print(f"   Number of nodes: {result.get('number', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

