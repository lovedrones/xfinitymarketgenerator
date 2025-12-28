"""
Simple test script to verify setup
"""
import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import gradio
        print("✅ gradio")
    except ImportError as e:
        print(f"❌ gradio: {e}")
        return False
    
    try:
        import PIL
        print("✅ PIL/Pillow")
    except ImportError as e:
        print(f"❌ PIL: {e}")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
    
    try:
        from huggingface_hub import hf_hub_download
        print("✅ huggingface_hub")
    except ImportError as e:
        print(f"❌ huggingface_hub: {e}")
        return False
    
    try:
        from workflow_loader import WorkflowLoader
        print("✅ workflow_loader")
    except ImportError as e:
        print(f"❌ workflow_loader: {e}")
        return False
    
    try:
        from comfyui_client import ComfyUIClient
        print("✅ comfyui_client")
    except ImportError as e:
        print(f"❌ comfyui_client: {e}")
        return False
    
    try:
        from model_loader import ModelLoader
        print("✅ model_loader")
    except ImportError as e:
        print(f"❌ model_loader: {e}")
        return False
    
    return True

def test_workflows():
    """Test that workflow files exist and can be loaded"""
    print("\nTesting workflows...")
    try:
        loader = WorkflowLoader(workflows_dir="workflows")
        
        if os.path.exists("workflows/basic.json"):
            workflow = loader.load_workflow("basic.json")
            print("✅ basic.json loaded")
        else:
            print("❌ basic.json not found")
            return False
        
        if os.path.exists("workflows/advanced.json"):
            workflow = loader.load_workflow("advanced.json")
            print("✅ advanced.json loaded")
        else:
            print("❌ advanced.json not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error loading workflows: {e}")
        return False

def test_model_loader():
    """Test model loader initialization"""
    print("\nTesting model loader...")
    try:
        loader = ModelLoader(cache_dir="models")
        print("✅ ModelLoader initialized")
        print(f"   Cache directory: {loader.cache_dir}")
        print(f"   Available models: {len(loader.model_mappings)}")
        return True
    except Exception as e:
        print(f"❌ Error initializing ModelLoader: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Product Photography Generator - Setup Test")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_workflows()
    all_passed &= test_model_loader()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Ensure ComfyUI is running (or will be started)")
        print("2. Run: python app.py")
        print("3. Open http://localhost:7860 in your browser")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

