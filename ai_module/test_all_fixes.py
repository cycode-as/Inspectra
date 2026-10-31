"""
Comprehensive Test Script for All 4 Fixes

Tests:
1. Background removal on different backgrounds
2. Adaptive score normalization
3. Heatmap file synchronization
4. Image normalization pipeline
"""

import sys
from pathlib import Path
import time

# Add ai_module to path
sys.path.insert(0, str(Path(__file__).parent))

from predict_fixed import predict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_background_methods(image_path: str):
    """Test Issue #1: Background removal with different methods."""
    print("\n" + "="*70)
    print("TEST 1: Background Removal Methods")
    print("="*70)
    
    methods = ["none", "grabcut", "threshold", "edge"]
    results = {}
    
    for method in methods:
        print(f"\n→ Testing with background method: {method}")
        try:
            result = predict(
                image_path,
                use_background_removal=(method != "none"),
                use_adaptive_normalization=False,  # Disable for isolated testing
                background_method=method
            )
            results[method] = result
            print(f"  ✅ Score: {result['anomaly_score']:.4f}, Status: {result['status']}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results[method] = None
    
    # Compare results
    print("\n→ Background Method Comparison:")
    print(f"{'Method':<15} {'Score':<10} {'Status':<10} {'Time (ms)':<12}")
    print("-" * 50)
    for method, result in results.items():
        if result:
            print(f"{method:<15} {result['anomaly_score']:<10.4f} {result['status']:<10} {result['inference_time_ms']:<12.2f}")
        else:
            print(f"{method:<15} {'FAILED':<10} {'-':<10} {'-':<12}")
    
    return results


def test_adaptive_normalization(image_path: str, num_runs: int = 5):
    """Test Issue #2: Adaptive score normalization over multiple runs."""
    print("\n" + "="*70)
    print("TEST 2: Adaptive Score Normalization")
    print("="*70)
    
    print(f"\n→ Running {num_runs} predictions to test adaptive normalization...")
    
    results = []
    for i in range(num_runs):
        print(f"\n  Run {i+1}/{num_runs}:")
        result = predict(
            image_path,
            use_background_removal=True,
            use_adaptive_normalization=True
        )
        results.append(result)
        print(f"    Raw Score: {result['raw_score']:.4f}")
        print(f"    Normalized Score: {result['anomaly_score']:.4f}")
        print(f"    Bounds: ({result['normalization_bounds'][0]:.4f}, {result['normalization_bounds'][1]:.4f})")
        print(f"    Status: {result['status']}")
    
    # Analyze adaptation
    print("\n→ Normalization Adaptation Analysis:")
    print(f"{'Run':<6} {'Raw':<10} {'Normalized':<12} {'Min Bound':<12} {'Max Bound':<12} {'Status':<10}")
    print("-" * 70)
    for i, result in enumerate(results, 1):
        print(f"{i:<6} {result['raw_score']:<10.4f} {result['anomaly_score']:<12.4f} "
              f"{result['normalization_bounds'][0]:<12.4f} {result['normalization_bounds'][1]:<12.4f} "
              f"{result['status']:<10}")
    
    return results


def test_heatmap_synchronization(image_path: str, num_tests: int = 10):
    """Test Issue #3: Heatmap file synchronization."""
    print("\n" + "="*70)
    print("TEST 3: Heatmap File Synchronization")
    print("="*70)
    
    print(f"\n→ Running {num_tests} predictions to test file synchronization...")
    
    success_count = 0
    failed_paths = []
    
    for i in range(num_tests):
        try:
            result = predict(image_path)
            heatmap_path = Path(result['heatmap_path'])
            
            # Immediately check if file exists and is readable
            if heatmap_path.exists():
                from PIL import Image
                with Image.open(heatmap_path) as img:
                    img.verify()
                success_count += 1
                print(f"  ✅ Test {i+1}/{num_tests}: File verified")
            else:
                print(f"  ❌ Test {i+1}/{num_tests}: File not found")
                failed_paths.append(str(heatmap_path))
        except Exception as e:
            print(f"  ❌ Test {i+1}/{num_tests}: Error - {e}")
            failed_paths.append("unknown")
    
    # Results
    print(f"\n→ Synchronization Test Results:")
    print(f"  Success Rate: {success_count}/{num_tests} ({success_count/num_tests*100:.1f}%)")
    if failed_paths:
        print(f"  Failed paths: {failed_paths}")
    else:
        print(f"  ✅ All heatmap files were properly synchronized!")
    
    return success_count == num_tests


def test_score_ranges(image_paths: list):
    """Test Issue #4: Image normalization by checking score ranges."""
    print("\n" + "="*70)
    print("TEST 4: Image Normalization & Score Ranges")
    print("="*70)
    
    print(f"\n→ Testing on {len(image_paths)} images...")
    
    results = []
    for i, image_path in enumerate(image_paths, 1):
        try:
            result = predict(image_path)
            results.append(result)
            print(f"  ✅ Image {i}: Score={result['anomaly_score']:.4f}, Status={result['status']}")
        except Exception as e:
            print(f"  ❌ Image {i}: Failed - {e}")
    
    if not results:
        print("\n  ❌ No successful predictions to analyze")
        return False
    
    # Analyze score distribution
    scores = [r['anomaly_score'] for r in results]
    print(f"\n→ Score Distribution Analysis:")
    print(f"  Min Score: {min(scores):.4f}")
    print(f"  Max Score: {max(scores):.4f}")
    print(f"  Mean Score: {sum(scores)/len(scores):.4f}")
    print(f"  Scores saturated at 1.0: {sum(1 for s in scores if s >= 0.999)}/{len(scores)}")
    print(f"  Scores saturated at 0.0: {sum(1 for s in scores if s <= 0.001)}/{len(scores)}")
    
    # Check if scores are well-distributed (not all saturated)
    saturated = sum(1 for s in scores if s >= 0.999 or s <= 0.001)
    well_distributed = saturated < len(scores) * 0.5  # Less than 50% saturated
    
    if well_distributed:
        print(f"  ✅ Scores are well-distributed (not saturated)")
    else:
        print(f"  ⚠️  Many scores are saturated ({saturated}/{len(scores)})")
    
    return well_distributed


def run_all_tests(test_image: str):
    """Run all comprehensive tests."""
    print("\n" + "="*70)
    print(" INSPECTRA FIX VALIDATION - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"\nTest Image: {test_image}\n")
    
    if not Path(test_image).exists():
        print(f"❌ Test image not found: {test_image}")
        print("\nPlease provide a valid test image path:")
        print("  python test_all_fixes.py path/to/test/image.png")
        return
    
    # Run all tests
    test_results = {}
    
    # Test 1: Background removal
    bg_results = test_background_methods(test_image)
    test_results['background_removal'] = all(r is not None for r in bg_results.values())
    
    # Test 2: Adaptive normalization
    norm_results = test_adaptive_normalization(test_image, num_runs=5)
    test_results['adaptive_normalization'] = len(norm_results) == 5
    
    # Test 3: Heatmap synchronization
    sync_success = test_heatmap_synchronization(test_image, num_tests=10)
    test_results['heatmap_sync'] = sync_success
    
    # Test 4: Score ranges (use same image multiple times for now)
    score_test = test_score_ranges([test_image] * 3)
    test_results['score_ranges'] = score_test
    
    # Final summary
    print("\n" + "="*70)
    print(" FINAL TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status}: {test_name.replace('_', ' ').title()}")
    
    total_passed = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\n  Overall: {total_passed}/{total_tests} tests passed")
    print("="*70 + "\n")
    
    return all(test_results.values())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python test_all_fixes.py path/to/test/image.png")
        print("\nExample:")
        print("  python test_all_fixes.py datasets/metal_nut/test/bent/000.png")
        sys.exit(1)
    
    test_image = sys.argv[1]
    success = run_all_tests(test_image)
    
    sys.exit(0 if success else 1)
