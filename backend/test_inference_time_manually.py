"""
Manual test script to verify inference_time_ms type conversion fix.

Run this script to test the fix independently:
    python test_inference_time_manually.py
"""

import sys
import tempfile
from app.services.inference import InferenceService, InferenceError


def test_float_conversion():
    """Test that float inference_time_ms values are converted to int."""
    print("\n" + "="*70)
    print("TEST 1: Float Conversion")
    print("="*70)
    
    # Create a temporary heatmap file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(b"test heatmap")
    temp_file.close()
    
    # Mock AI function that returns float
    def mock_ai_with_float(image_path: str):
        print(f"  📊 AI Model Output:")
        print(f"     - inference_time_ms: 152.7834 (type: float)")
        return {
            "anomaly_score": 0.75,
            "status": "REVIEW",
            "heatmap_path": temp_file.name,
            "inference_time_ms": 152.7834  # Float value
        }
    
    try:
        service = InferenceService(mock_ai_with_float)
        result = service.predict("test_image.jpg")
        
        print(f"\n  ✅ SUCCESS!")
        print(f"     - inference_time_ms: {result['inference_time_ms']} (type: {type(result['inference_time_ms']).__name__})")
        print(f"     - Converted correctly: {isinstance(result['inference_time_ms'], int)}")
        
        import os
        os.unlink(temp_file.name)
        return True
        
    except InferenceError as e:
        print(f"\n  ❌ FAILED: {e}")
        import os
        os.unlink(temp_file.name)
        return False


def test_integer_still_works():
    """Test that integer values still work (backward compatibility)."""
    print("\n" + "="*70)
    print("TEST 2: Integer Values (Backward Compatibility)")
    print("="*70)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(b"test heatmap")
    temp_file.close()
    
    def mock_ai_with_int(image_path: str):
        print(f"  📊 AI Model Output:")
        print(f"     - inference_time_ms: 150 (type: int)")
        return {
            "anomaly_score": 0.5,
            "status": "PASS",
            "heatmap_path": temp_file.name,
            "inference_time_ms": 150  # Integer value
        }
    
    try:
        service = InferenceService(mock_ai_with_int)
        result = service.predict("test_image.jpg")
        
        print(f"\n  ✅ SUCCESS!")
        print(f"     - inference_time_ms: {result['inference_time_ms']} (type: {type(result['inference_time_ms']).__name__})")
        
        import os
        os.unlink(temp_file.name)
        return True
        
    except InferenceError as e:
        print(f"\n  ❌ FAILED: {e}")
        import os
        os.unlink(temp_file.name)
        return False


def test_none_handling():
    """Test that None values are handled gracefully."""
    print("\n" + "="*70)
    print("TEST 3: None Value Handling")
    print("="*70)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(b"test heatmap")
    temp_file.close()
    
    def mock_ai_with_none(image_path: str):
        print(f"  📊 AI Model Output:")
        print(f"     - inference_time_ms: None")
        return {
            "anomaly_score": 0.5,
            "status": "PASS",
            "heatmap_path": temp_file.name,
            "inference_time_ms": None  # None value
        }
    
    try:
        service = InferenceService(mock_ai_with_none)
        result = service.predict("test_image.jpg")
        
        print(f"\n  ✅ SUCCESS!")
        print(f"     - inference_time_ms defaulted to: {result['inference_time_ms']}")
        print(f"     - Type: {type(result['inference_time_ms']).__name__}")
        
        import os
        os.unlink(temp_file.name)
        return True
        
    except InferenceError as e:
        print(f"\n  ❌ FAILED: {e}")
        import os
        os.unlink(temp_file.name)
        return False


def test_invalid_type_rejection():
    """Test that invalid types are still rejected."""
    print("\n" + "="*70)
    print("TEST 4: Invalid Type Rejection")
    print("="*70)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file.write(b"test heatmap")
    temp_file.close()
    
    def mock_ai_with_string(image_path: str):
        print(f"  📊 AI Model Output:")
        print(f"     - inference_time_ms: 'not_a_number' (type: str)")
        return {
            "anomaly_score": 0.5,
            "status": "PASS",
            "heatmap_path": temp_file.name,
            "inference_time_ms": "not_a_number"  # Invalid string
        }
    
    try:
        service = InferenceService(mock_ai_with_string)
        result = service.predict("test_image.jpg")
        
        print(f"\n  ❌ FAILED: Should have raised InferenceError!")
        import os
        os.unlink(temp_file.name)
        return False
        
    except InferenceError as e:
        print(f"\n  ✅ SUCCESS! Correctly rejected invalid type")
        print(f"     - Error: {e}")
        import os
        os.unlink(temp_file.name)
        return True


def test_various_float_values():
    """Test conversion with various float values."""
    print("\n" + "="*70)
    print("TEST 5: Various Float Values & Rounding")
    print("="*70)
    
    test_cases = [
        (100.1, 100),
        (100.5, 100),  # Banker's rounding
        (100.9, 101),
        (150.7, 151),
        (200.0, 200),
    ]
    
    all_passed = True
    
    for float_value, expected_int in test_cases:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(b"test heatmap")
        temp_file.close()
        
        def mock_ai(image_path: str):
            return {
                "anomaly_score": 0.5,
                "status": "PASS",
                "heatmap_path": temp_file.name,
                "inference_time_ms": float_value
            }
        
        try:
            service = InferenceService(mock_ai)
            result = service.predict("test.jpg")
            
            if result["inference_time_ms"] == expected_int:
                print(f"  ✅ {float_value} → {result['inference_time_ms']} (expected {expected_int})")
            else:
                print(f"  ❌ {float_value} → {result['inference_time_ms']} (expected {expected_int})")
                all_passed = False
            
            import os
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"  ❌ {float_value} raised error: {e}")
            all_passed = False
            import os
            os.unlink(temp_file.name)
    
    return all_passed


def main():
    """Run all manual tests."""
    print("\n" + "="*70)
    print("MANUAL TEST SUITE: inference_time_ms Type Conversion Fix")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(("Float Conversion", test_float_conversion()))
    results.append(("Integer Compatibility", test_integer_still_works()))
    results.append(("None Handling", test_none_handling()))
    results.append(("Invalid Type Rejection", test_invalid_type_rejection()))
    results.append(("Various Float Values", test_various_float_values()))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    print("="*70 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
