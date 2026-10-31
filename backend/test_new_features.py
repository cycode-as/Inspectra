"""
Comprehensive API Testing Script for New Features

Tests all newly implemented features:
- Feedback system
- Analytics (summary and trends)
- PDF report generation
- QR code generation
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_health():
    """Test health endpoint."""
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_feedback_create(inspection_id=1):
    """Test creating feedback."""
    print_section("2. Create Feedback")
    
    payload = {
        "inspection_id": inspection_id,
        "feedback_type": "Correct prediction",
        "comments": "The AI correctly identified the defect. Great work!"
    }
    
    print(f"POST {BASE_URL}/api/feedback")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 201:
        print(f"✅ Feedback created successfully!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_feedback_list():
    """Test listing feedback."""
    print_section("3. List All Feedback")
    
    response = requests.get(f"{BASE_URL}/api/feedback")
    print(f"GET {BASE_URL}/api/feedback")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        feedback_list = response.json()
        print(f"✅ Retrieved {len(feedback_list)} feedback record(s)")
        
        for i, feedback in enumerate(feedback_list[:3], 1):
            print(f"\n[{i}] Feedback ID: {feedback['id']}")
            print(f"    Inspection ID: {feedback['inspection_id']}")
            print(f"    Type: {feedback['feedback_type']}")
            print(f"    Comments: {feedback.get('comments', 'N/A')}")
            print(f"    Created: {feedback['created_at']}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_analytics_summary():
    """Test analytics summary endpoint."""
    print_section("4. Analytics Summary")
    
    response = requests.get(f"{BASE_URL}/api/analytics/summary")
    print(f"GET {BASE_URL}/api/analytics/summary")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        summary = response.json()
        print(f"✅ Analytics Summary:")
        print(f"   Total Inspections: {summary['total_inspections']}")
        print(f"   PASS Count: {summary['pass_count']}")
        print(f"   REVIEW Count: {summary['review_count']}")
        print(f"   REJECT Count: {summary['reject_count']}")
        print(f"   Defect Rate: {summary['defect_rate']}%")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_analytics_trends():
    """Test analytics trends endpoint."""
    print_section("5. Analytics Trends")
    
    response = requests.get(f"{BASE_URL}/api/analytics/trends")
    print(f"GET {BASE_URL}/api/analytics/trends")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        trends = response.json()['trends']
        print(f"✅ Retrieved {len(trends)} day(s) of trends")
        
        for i, trend in enumerate(trends[:5], 1):
            print(f"\n[{i}] Date: {trend['date']}")
            print(f"    Total: {trend['total']}")
            print(f"    PASS: {trend['pass_count']} | REVIEW: {trend['review_count']} | REJECT: {trend['reject_count']}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_pdf_report(inspection_id=1):
    """Test PDF report generation."""
    print_section("6. Generate PDF Report")
    
    response = requests.get(f"{BASE_URL}/api/inspections/{inspection_id}/report")
    print(f"GET {BASE_URL}/api/inspections/{inspection_id}/report")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ PDF report generated successfully!")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   File Size: {len(response.content)} bytes")
        
        # Optionally save the PDF
        filename = f"test_report_{inspection_id}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"   Saved to: {filename}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def test_qr_code(inspection_id=1):
    """Test QR code generation."""
    print_section("7. Generate QR Code")
    
    response = requests.get(f"{BASE_URL}/api/inspections/{inspection_id}/qr")
    print(f"GET {BASE_URL}/api/inspections/{inspection_id}/qr")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ QR code generated successfully!")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   File Size: {len(response.content)} bytes")
        
        # Optionally save the QR code
        filename = f"test_qr_{inspection_id}.png"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"   Saved to: {filename}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  INSPECTRA NEW FEATURES TEST SUITE")
    print("  Testing: Feedback, Analytics, PDF Reports, QR Codes")
    print("=" * 70)
    
    # Check if server is running
    try:
        print("\nChecking if backend server is running...")
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"✅ Backend is running at {BASE_URL}")
    except requests.exceptions.RequestException:
        print(f"\n❌ Backend is not running at {BASE_URL}")
        print("\nPlease start the backend server first:")
        print("  cd backend")
        print("  .\\venv\\Scripts\\Activate.ps1")
        print("  uvicorn main:app --reload")
        return
    
    # Run all tests
    results = []
    
    results.append(("Health Check", test_health()))
    results.append(("Create Feedback", test_feedback_create()))
    results.append(("List Feedback", test_feedback_list()))
    results.append(("Analytics Summary", test_analytics_summary()))
    results.append(("Analytics Trends", test_analytics_trends()))
    results.append(("PDF Report Generation", test_pdf_report()))
    results.append(("QR Code Generation", test_qr_code()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
