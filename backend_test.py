#!/usr/bin/env python3
"""
Backend API Test Suite for Copper Strip ASTM D130 Module
Tests all /api/copper/* endpoints including AI Vision analysis
"""
import os
import sys
import time
import json
import requests
from pathlib import Path

# Load backend URL from frontend .env
env_file = Path("/app/frontend/.env")
BACKEND_URL = "https://web-app-rating.preview.emergentagent.com"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            BACKEND_URL = line.split("=", 1)[1].strip()
            break

BASE_URL = f"{BACKEND_URL}/api"
print(f"Testing backend at: {BASE_URL}")

# Valid ASTM D130 classification codes
VALID_CLASSIFICATIONS = ["0", "1a", "1b", "2a", "2b", "2c", "2d", "3a", "3b", "3c", "4a", "4b", "4c"]
CLEAR_CODES = ["0", "1a", "1b"]

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_pass(test_name):
    print(f"✅ PASS: {test_name}")
    test_results["passed"].append(test_name)

def log_fail(test_name, reason):
    print(f"❌ FAIL: {test_name}")
    print(f"   Reason: {reason}")
    test_results["failed"].append({"test": test_name, "reason": reason})

def log_warning(test_name, message):
    print(f"⚠️  WARNING: {test_name}")
    print(f"   Message: {message}")
    test_results["warnings"].append({"test": test_name, "message": message})

def test_copper_dashboard():
    """Test GET /api/copper/dashboard"""
    try:
        resp = requests.get(f"{BASE_URL}/copper/dashboard", timeout=10)
        if resp.status_code != 200:
            log_fail("GET /api/copper/dashboard", f"Status {resp.status_code}: {resp.text}")
            return None
        
        data = resp.json()
        
        # Verify structure
        required_keys = ["latest", "total", "passed", "failed"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            log_fail("GET /api/copper/dashboard", f"Missing keys: {missing}")
            return None
        
        # Verify total >= 4 (seeded records)
        if data["total"] < 4:
            log_fail("GET /api/copper/dashboard", f"Expected total >= 4, got {data['total']}")
            return None
        
        # Verify passed + failed == total
        if data["passed"] + data["failed"] != data["total"]:
            log_fail("GET /api/copper/dashboard", 
                    f"passed ({data['passed']}) + failed ({data['failed']}) != total ({data['total']})")
            return None
        
        log_pass("GET /api/copper/dashboard")
        return data
    except Exception as e:
        log_fail("GET /api/copper/dashboard", str(e))
        return None

def test_copper_trend():
    """Test GET /api/copper/trend"""
    try:
        resp = requests.get(f"{BASE_URL}/copper/trend", timeout=10)
        if resp.status_code != 200:
            log_fail("GET /api/copper/trend", f"Status {resp.status_code}: {resp.text}")
            return None
        
        data = resp.json()
        
        if not isinstance(data, list):
            log_fail("GET /api/copper/trend", f"Expected list, got {type(data)}")
            return None
        
        # Verify each point has required fields
        required_fields = ["id", "classification", "severity", "status", "sample_id", "created_at"]
        for i, point in enumerate(data):
            missing = [f for f in required_fields if f not in point]
            if missing:
                log_fail("GET /api/copper/trend", f"Point {i} missing fields: {missing}")
                return None
            
            # Verify severity is 0-12
            if not (0 <= point["severity"] <= 12):
                log_fail("GET /api/copper/trend", f"Point {i} severity {point['severity']} not in range 0-12")
                return None
        
        log_pass("GET /api/copper/trend")
        return data
    except Exception as e:
        log_fail("GET /api/copper/trend", str(e))
        return None

def test_copper_tests_list():
    """Test GET /api/copper/tests"""
    try:
        resp = requests.get(f"{BASE_URL}/copper/tests", timeout=10)
        if resp.status_code != 200:
            log_fail("GET /api/copper/tests", f"Status {resp.status_code}: {resp.text}")
            return None
        
        data = resp.json()
        
        if not isinstance(data, list):
            log_fail("GET /api/copper/tests", f"Expected list, got {type(data)}")
            return None
        
        # Verify >= 4 seeded records
        if len(data) < 4:
            log_fail("GET /api/copper/tests", f"Expected >= 4 records, got {len(data)}")
            return None
        
        log_pass("GET /api/copper/tests")
        return data
    except Exception as e:
        log_fail("GET /api/copper/tests", str(e))
        return None

def test_copper_tests_search():
    """Test GET /api/copper/tests?q=Diesel"""
    try:
        resp = requests.get(f"{BASE_URL}/copper/tests", params={"q": "Diesel"}, timeout=10)
        if resp.status_code != 200:
            log_fail("GET /api/copper/tests?q=Diesel", f"Status {resp.status_code}: {resp.text}")
            return None
        
        data = resp.json()
        
        if not isinstance(data, list):
            log_fail("GET /api/copper/tests?q=Diesel", f"Expected list, got {type(data)}")
            return None
        
        # Should have at least one result (seeded data has "Diesel Fuel B30")
        if len(data) == 0:
            log_warning("GET /api/copper/tests?q=Diesel", "No results found for 'Diesel' search")
        
        log_pass("GET /api/copper/tests?q=Diesel")
        return data
    except Exception as e:
        log_fail("GET /api/copper/tests?q=Diesel", str(e))
        return None

def test_copper_reference_scale():
    """Test GET /api/copper/reference-scale"""
    try:
        resp = requests.get(f"{BASE_URL}/copper/reference-scale", timeout=10)
        if resp.status_code != 200:
            log_fail("GET /api/copper/reference-scale", f"Status {resp.status_code}: {resp.text}")
            return None
        
        data = resp.json()
        
        # Verify structure
        required_keys = ["title", "note", "image", "classes"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            log_fail("GET /api/copper/reference-scale", f"Missing keys: {missing}")
            return None
        
        # Verify image is base64 data URI
        if not data["image"].startswith("data:image/"):
            log_fail("GET /api/copper/reference-scale", "Image is not a base64 data URI")
            return None
        
        # Verify 13 classes
        if len(data["classes"]) != 13:
            log_fail("GET /api/copper/reference-scale", f"Expected 13 classes, got {len(data['classes'])}")
            return None
        
        log_pass("GET /api/copper/reference-scale")
        return data
    except Exception as e:
        log_fail("GET /api/copper/reference-scale", str(e))
        return None

def test_copper_get_by_id(test_id):
    """Test GET /api/copper/tests/{id}"""
    try:
        resp = requests.get(f"{BASE_URL}/copper/tests/{test_id}", timeout=10)
        if resp.status_code != 200:
            log_fail(f"GET /api/copper/tests/{test_id}", f"Status {resp.status_code}: {resp.text}")
            return None
        
        data = resp.json()
        
        # Verify it has the expected ID
        if data.get("id") != test_id:
            log_fail(f"GET /api/copper/tests/{test_id}", f"ID mismatch: expected {test_id}, got {data.get('id')}")
            return None
        
        log_pass(f"GET /api/copper/tests/{test_id}")
        return data
    except Exception as e:
        log_fail(f"GET /api/copper/tests/{test_id}", str(e))
        return None

def test_copper_get_invalid_id():
    """Test GET /api/copper/tests/{invalid_id} returns 404"""
    try:
        invalid_id = "invalid-test-id-12345"
        resp = requests.get(f"{BASE_URL}/copper/tests/{invalid_id}", timeout=10)
        if resp.status_code != 404:
            log_fail("GET /api/copper/tests/{invalid_id} → 404", 
                    f"Expected 404, got {resp.status_code}")
            return False
        
        log_pass("GET /api/copper/tests/{invalid_id} → 404")
        return True
    except Exception as e:
        log_fail("GET /api/copper/tests/{invalid_id} → 404", str(e))
        return False

def test_upload_image():
    """Test POST /api/kht/upload"""
    try:
        # Create a minimal JPEG image (1x1 pixel)
        jpeg_data = bytes.fromhex(
            'ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707'
            '07090909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c'
            '231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b'
            '0c180d0d1832211c213232323232323232323232323232323232323232323232323232'
            '32323232323232323232323232323232323232323232323232ffc00011080001000103'
            '012200021101031101ffc4001500010100000000000000000000000000000000ffc400'
            '14100100000000000000000000000000000000ffc40014010100000000000000000000'
            '000000000000ffc40014110100000000000000000000000000000000ffda000c030100'
            '02110311003f00bf800000ffd9'
        )
        
        files = {"file": ("test_copper.jpg", jpeg_data, "image/jpeg")}
        resp = requests.post(f"{BASE_URL}/kht/upload", files=files, timeout=30)
        
        if resp.status_code != 200:
            log_fail("POST /api/kht/upload", f"Status {resp.status_code}: {resp.text}")
            return None
        
        data = resp.json()
        
        if "image_path" not in data:
            log_fail("POST /api/kht/upload", "Response missing 'image_path'")
            return None
        
        log_pass("POST /api/kht/upload")
        return data["image_path"]
    except Exception as e:
        log_fail("POST /api/kht/upload", str(e))
        return None

def test_copper_analyze_full_flow():
    """Test full AI Vision analysis flow: upload → analyze → poll → verify"""
    print("\n=== Testing Full AI Vision Analysis Flow ===")
    
    # Step 1: Upload image
    image_path = test_upload_image()
    if not image_path:
        log_fail("Full AI Vision Flow", "Failed to upload image")
        return None
    
    # Step 2: Start analysis
    try:
        payload = {
            "image_path": image_path,
            "sample_id": "CU-TEST-001",
            "product": "Diesel Fuel B30",
            "batch": "LOT-TEST",
            "operator": "Tester",
            "temperature_c": 100,
            "duration_hours": 3,
            "remark": ""
        }
        
        resp = requests.post(f"{BASE_URL}/copper/analyze/start", json=payload, timeout=30)
        
        if resp.status_code != 200:
            log_fail("POST /api/copper/analyze/start", f"Status {resp.status_code}: {resp.text}")
            return None
        
        job = resp.json()
        
        if "id" not in job or "status" not in job:
            log_fail("POST /api/copper/analyze/start", "Response missing 'id' or 'status'")
            return None
        
        if job["status"] != "running":
            log_fail("POST /api/copper/analyze/start", f"Expected status 'running', got '{job['status']}'")
            return None
        
        log_pass("POST /api/copper/analyze/start")
        job_id = job["id"]
        
    except Exception as e:
        log_fail("POST /api/copper/analyze/start", str(e))
        return None
    
    # Step 3: Poll job status (allow up to 2 minutes for real AI call)
    print(f"Polling job {job_id} (allowing up to 120 seconds for AI analysis)...")
    max_wait = 120
    poll_interval = 3
    elapsed = 0
    record_id = None
    
    while elapsed < max_wait:
        try:
            resp = requests.get(f"{BASE_URL}/copper/analyze/jobs/{job_id}", timeout=10)
            
            if resp.status_code != 200:
                log_fail(f"GET /api/copper/analyze/jobs/{job_id}", f"Status {resp.status_code}: {resp.text}")
                return None
            
            job_status = resp.json()
            status = job_status.get("status")
            
            print(f"  [{elapsed}s] Job status: {status}")
            
            if status == "done":
                record_id = job_status.get("record_id")
                if not record_id:
                    log_fail("Job polling", "Job done but no record_id")
                    return None
                log_pass(f"GET /api/copper/analyze/jobs/{job_id} → done")
                break
            elif status == "error":
                error = job_status.get("error", "Unknown error")
                log_fail("Job polling", f"Job failed with error: {error}")
                return None
            elif status != "running":
                log_fail("Job polling", f"Unexpected status: {status}")
                return None
            
            time.sleep(poll_interval)
            elapsed += poll_interval
            
        except Exception as e:
            log_fail("Job polling", str(e))
            return None
    
    if not record_id:
        log_fail("Job polling", f"Job did not complete within {max_wait} seconds")
        return None
    
    # Step 4: Verify the created record
    try:
        resp = requests.get(f"{BASE_URL}/copper/tests/{record_id}", timeout=10)
        
        if resp.status_code != 200:
            log_fail(f"GET /api/copper/tests/{record_id}", f"Status {resp.status_code}: {resp.text}")
            return None
        
        record = resp.json()
        
        # Verify classification is valid
        classification = record.get("classification")
        if classification not in VALID_CLASSIFICATIONS:
            log_fail("AI Vision result validation", 
                    f"Invalid classification '{classification}', expected one of {VALID_CLASSIFICATIONS}")
            return None
        
        # Verify status consistency
        status = record.get("status")
        expected_status = "CLEAR" if classification in CLEAR_CODES else "TARNISH"
        if status != expected_status:
            log_fail("AI Vision result validation", 
                    f"Status '{status}' inconsistent with classification '{classification}' (expected '{expected_status}')")
            return None
        
        # Verify confidence is 0-100
        confidence = record.get("confidence", 0)
        if not (0 <= confidence <= 100):
            log_fail("AI Vision result validation", f"Confidence {confidence} not in range 0-100")
            return None
        
        # Verify ai_summary is present
        if not record.get("ai_summary"):
            log_warning("AI Vision result validation", "ai_summary is empty")
        
        log_pass("AI Vision result validation (classification, status, confidence)")
        return record_id
        
    except Exception as e:
        log_fail("AI Vision result validation", str(e))
        return None

def test_copper_analyze_invalid_image():
    """Test POST /api/copper/analyze/start with non-existent image_path → 404"""
    try:
        payload = {
            "image_path": "non-existent-path/fake-image.jpg",
            "sample_id": "CU-TEST-INVALID",
            "product": "Test Product",
            "batch": "TEST",
            "operator": "Tester",
            "temperature_c": 100,
            "duration_hours": 3,
            "remark": ""
        }
        
        resp = requests.post(f"{BASE_URL}/copper/analyze/start", json=payload, timeout=30)
        
        if resp.status_code != 404:
            log_fail("POST /api/copper/analyze/start (invalid image) → 404", 
                    f"Expected 404, got {resp.status_code}")
            return False
        
        log_pass("POST /api/copper/analyze/start (invalid image) → 404")
        return True
    except Exception as e:
        log_fail("POST /api/copper/analyze/start (invalid image) → 404", str(e))
        return False

def test_copper_update_classification(test_id):
    """Test PUT /api/copper/tests/{id} with classification update"""
    try:
        payload = {"classification": "4b"}
        resp = requests.put(f"{BASE_URL}/copper/tests/{test_id}", json=payload, timeout=10)
        
        if resp.status_code != 200:
            log_fail(f"PUT /api/copper/tests/{test_id} (classification)", 
                    f"Status {resp.status_code}: {resp.text}")
            return None
        
        data = resp.json()
        
        # Verify classification updated
        if data.get("classification") != "4b":
            log_fail(f"PUT /api/copper/tests/{test_id} (classification)", 
                    f"Classification not updated: {data.get('classification')}")
            return None
        
        # Verify status is TARNISH (4b is corrosion)
        if data.get("status") != "TARNISH":
            log_fail(f"PUT /api/copper/tests/{test_id} (classification)", 
                    f"Status should be TARNISH, got {data.get('status')}")
            return None
        
        # Verify severity is 11 (4b severity)
        if data.get("severity") != 11:
            log_fail(f"PUT /api/copper/tests/{test_id} (classification)", 
                    f"Severity should be 11, got {data.get('severity')}")
            return None
        
        # Verify group is "Corrosion"
        if data.get("group") != "Corrosion":
            log_fail(f"PUT /api/copper/tests/{test_id} (classification)", 
                    f"Group should be 'Corrosion', got {data.get('group')}")
            return None
        
        # Verify edited flag
        if not data.get("edited"):
            log_warning(f"PUT /api/copper/tests/{test_id} (classification)", 
                       "edited flag not set to true")
        
        log_pass(f"PUT /api/copper/tests/{test_id} (classification → 4b, status → TARNISH, severity → 11)")
        return data
    except Exception as e:
        log_fail(f"PUT /api/copper/tests/{test_id} (classification)", str(e))
        return None

def test_copper_update_text_fields(test_id):
    """Test PUT /api/copper/tests/{id} with ai_summary and recommendation"""
    try:
        payload = {
            "ai_summary": "koreksi manual",
            "recommendation": "ganti bahan bakar"
        }
        resp = requests.put(f"{BASE_URL}/copper/tests/{test_id}", json=payload, timeout=10)
        
        if resp.status_code != 200:
            log_fail(f"PUT /api/copper/tests/{test_id} (text fields)", 
                    f"Status {resp.status_code}: {resp.text}")
            return None
        
        data = resp.json()
        
        # Verify fields updated
        if data.get("ai_summary") != "koreksi manual":
            log_fail(f"PUT /api/copper/tests/{test_id} (text fields)", 
                    f"ai_summary not updated: {data.get('ai_summary')}")
            return None
        
        if data.get("recommendation") != "ganti bahan bakar":
            log_fail(f"PUT /api/copper/tests/{test_id} (text fields)", 
                    f"recommendation not updated: {data.get('recommendation')}")
            return None
        
        log_pass(f"PUT /api/copper/tests/{test_id} (ai_summary, recommendation)")
        
        # Verify persistence by fetching again
        resp2 = requests.get(f"{BASE_URL}/copper/tests/{test_id}", timeout=10)
        if resp2.status_code == 200:
            data2 = resp2.json()
            if (data2.get("ai_summary") == "koreksi manual" and 
                data2.get("recommendation") == "ganti bahan bakar"):
                log_pass(f"PUT /api/copper/tests/{test_id} (persistence verified)")
            else:
                log_fail(f"PUT /api/copper/tests/{test_id} (persistence)", 
                        "Updated fields not persisted")
        
        return data
    except Exception as e:
        log_fail(f"PUT /api/copper/tests/{test_id} (text fields)", str(e))
        return None

def test_copper_delete(test_id):
    """Test DELETE /api/copper/tests/{id}"""
    try:
        resp = requests.delete(f"{BASE_URL}/copper/tests/{test_id}", timeout=10)
        
        if resp.status_code != 200:
            log_fail(f"DELETE /api/copper/tests/{test_id}", 
                    f"Status {resp.status_code}: {resp.text}")
            return False
        
        data = resp.json()
        
        if not data.get("ok"):
            log_fail(f"DELETE /api/copper/tests/{test_id}", 
                    f"Response should have ok:true, got {data}")
            return False
        
        log_pass(f"DELETE /api/copper/tests/{test_id}")
        
        # Verify it's gone from list
        resp2 = requests.get(f"{BASE_URL}/copper/tests", timeout=10)
        if resp2.status_code == 200:
            tests = resp2.json()
            if any(t.get("id") == test_id for t in tests):
                log_fail(f"DELETE /api/copper/tests/{test_id} (list check)", 
                        "Deleted record still appears in list")
                return False
            log_pass(f"DELETE /api/copper/tests/{test_id} (removed from list)")
        
        # Verify GET returns 404
        resp3 = requests.get(f"{BASE_URL}/copper/tests/{test_id}", timeout=10)
        if resp3.status_code != 404:
            log_fail(f"DELETE /api/copper/tests/{test_id} (404 check)", 
                    f"Expected 404, got {resp3.status_code}")
            return False
        log_pass(f"DELETE /api/copper/tests/{test_id} (GET returns 404)")
        
        return True
    except Exception as e:
        log_fail(f"DELETE /api/copper/tests/{test_id}", str(e))
        return False

def main():
    print("=" * 80)
    print("COPPER STRIP ASTM D130 BACKEND API TEST SUITE")
    print("=" * 80)
    print()
    
    # 1. Read-only endpoints
    print("=== Testing Read-Only Endpoints ===")
    dashboard = test_copper_dashboard()
    trend = test_copper_trend()
    tests = test_copper_tests_list()
    test_copper_tests_search()
    reference = test_copper_reference_scale()
    
    # Get a valid test ID from the list
    valid_test_id = None
    if tests and len(tests) > 0:
        valid_test_id = tests[0]["id"]
        test_copper_get_by_id(valid_test_id)
    
    test_copper_get_invalid_id()
    
    # 2. Full AI Vision analysis flow
    created_record_id = test_copper_analyze_full_flow()
    
    # 3. Test analyze with invalid image
    test_copper_analyze_invalid_image()
    
    # 4. Update tests (use the AI-created record if available, else use a seeded one)
    update_test_id = created_record_id if created_record_id else valid_test_id
    if update_test_id:
        print(f"\n=== Testing Update Operations (using record {update_test_id}) ===")
        test_copper_update_classification(update_test_id)
        test_copper_update_text_fields(update_test_id)
    else:
        log_warning("Update tests", "No test ID available for update tests")
    
    # 5. Delete test (only delete the AI-created test, not seeded demo records)
    if created_record_id:
        print(f"\n=== Testing Delete Operation (using AI-created record {created_record_id}) ===")
        test_copper_delete(created_record_id)
    else:
        log_warning("Delete test", "No AI-created record to delete (preserving seeded demo records)")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}")
    
    if test_results["failed"]:
        print("\nFailed Tests:")
        for fail in test_results["failed"]:
            print(f"  - {fail['test']}: {fail['reason']}")
    
    if test_results["warnings"]:
        print("\nWarnings:")
        for warn in test_results["warnings"]:
            print(f"  - {warn['test']}: {warn['message']}")
    
    print("\n" + "=" * 80)
    
    # Exit with appropriate code
    sys.exit(0 if len(test_results["failed"]) == 0 else 1)

if __name__ == "__main__":
    main()
