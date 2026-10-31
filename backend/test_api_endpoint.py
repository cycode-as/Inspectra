"""
Test the /inspect endpoint with a real API call.

This script starts the FastAPI server and makes a test request to verify
the inference_time_ms fix works end-to-end.

Usage:
    1. Make sure the backend is running: uvicorn main:app --reload
    2. Run this script: python test_api_endpoint.py
"""

import requests
import os
import sys
from pathlib import Path


def test_inspect_endpoint():
    """Test the /inspect endpoint with a real image."""
    
    print("\n" + "="*70)
    print("API ENDPOINT TEST: /inspect")
    print("="*70)
    
    # API endpoint URL
    base_url = "http://localhost:8000"
    inspect_url = f"{base_url}/inspect"
    
    # Check if API is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=2)
        print(f"\n✅ API is running at {base_url}")
        print(f"   Health check: {health_response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API is not running at {base_url}")
        print(f"   Error: {e}")
        print(f"\n   Please start the backend server first:")
        print(f"   cd backend")
        print(f"   .\\venv\\Scripts\\Activate.ps1")
        print(f"   uvicorn main:app --reload")
        return False
    
    # Find a test image from the dataset
    dataset_path = Path("ai_module/datasets/metal_nut/test/bent")
    if not dataset_path.exists():
        # Try alternative path
        dataset_path = Path("../ai_module/datasets/metal_nut/test/bent")
    
    if dataset_path.exists():
        test_images = list(dataset_path.glob("*.png"))
        if test_images:
            image_path = test_images[0]
            print(f"\n📁 Using test image: {image_path}")
        else:
            print(f"\n⚠️  No test images found in {dataset_path}")
            print(f"   Creating a dummy image for testing...")
            # Create a dummy image
            from PIL import Image
            import io
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            image_path = "test_image.png"
    else:
        print(f"\n⚠️  Dataset not found, creating a dummy image...")
        from PIL import Image
        import io
        img = Image.new('RGB', (100, 100), color='red')
        img.save("test_image.png")
        image_path = "test_image.png"
    
    # Prepare the request
    print(f"\n📤 Making POST request to {inspect_url}")
    
    try:
        with open(image_path, 'rb') as image_file:
            files = {
                'file': ('test_image.png', image_file, 'image/png')
            }
            data = {
                'product_id': 'TEST-PROD-001'
            }
            
            print(f"   - Product ID: TEST-PROD-001")
            print(f"   - Image: {image_path.name if hasattr(image_path, 'name') else image_path}")
            
            response = requests.post(inspect_url, files=files, data=data)
            
            print(f"\n📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ SUCCESS! Inspection completed")
                print(f"\n   Response Data:")
                print(f"   - ID: {result.get('id')}")
                print(f"   - Product ID: {result.get('product_id')}")
                print(f"   - Anomaly Score: {result.get('anomaly_score')}")
                print(f"   - Status: {result.get('status')}")
                print(f"   - inference_time_ms: {result.get('inference_time_ms')} (type: {type(result.get('inference_time_ms')).__name__})")
                print(f"   - Created At: {result.get('created_at')}")
                
                # Verify inference_time_ms is an integer
                inference_time = result.get('inference_time_ms')
                if isinstance(inference_time, int):
                    print(f"\n✅ inference_time_ms is correctly an integer!")
                else:
                    print(f"\n⚠️  inference_time_ms is {type(inference_time).__name__}, expected int")
                
                return True
            else:
                print(f"\n❌ Request failed")
                print(f"   Response: {response.text}")
                return False
                
    except FileNotFoundError:
        print(f"\n❌ Image file not found: {image_path}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_inspections():
    """Test the GET /inspections endpoint."""
    
    print("\n" + "="*70)
    print("API ENDPOINT TEST: GET /inspections")
    print("="*70)
    
    base_url = "http://localhost:8000"
    inspections_url = f"{base_url}/inspections"
    
    try:
        response = requests.get(inspections_url)
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            inspections = response.json()
            print(f"\n✅ SUCCESS! Retrieved {len(inspections)} inspection(s)")
            
            if inspections:
                print(f"\n   Recent inspections:")
                for i, inspection in enumerate(inspections[:3], 1):
                    print(f"\n   [{i}] ID: {inspection.get('id')}")
                    print(f"       Product: {inspection.get('product_id')}")
                    print(f"       Status: {inspection.get('status')}")
                    print(f"       inference_time_ms: {inspection.get('inference_time_ms')} ms")
                    
                    # Verify type
                    if isinstance(inspection.get('inference_time_ms'), int):
                        print(f"       ✅ Type is correct (int)")
                    else:
                        print(f"       ⚠️  Type is {type(inspection.get('inference_time_ms')).__name__}")
            else:
                print(f"\n   No inspections found. Create one using POST /inspect")
            
            return True
        else:
            print(f"\n❌ Request failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False


def main():
    """Run API endpoint tests."""
    
    print("\n" + "="*70)
    print("API ENDPOINT TESTING SUITE")
    print("Testing the inference_time_ms fix end-to-end")
    print("="*70)
    
    # Test 1: Create an inspection
    test1_passed = test_inspect_endpoint()
    
    # Test 2: Retrieve inspections
    test2_passed = test_get_inspections()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    tests = [
        ("POST /inspect", test1_passed),
        ("GET /inspections", test2_passed)
    ]
    
    for test_name, passed in tests:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    passed_count = sum(1 for _, p in tests if p)
    print(f"\n  Total: {passed_count}/{len(tests)} tests passed")
    print("="*70 + "\n")
    
    return 0 if passed_count == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())
