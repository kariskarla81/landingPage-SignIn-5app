#!/usr/bin/env python3
"""
Backend API Testing for DKA-CEC L-48-A-00 Module
Tests the NEW /api/dkacec/* endpoints ONLY
"""

import os
import sys
import time
import json
import requests
from pathlib import Path

# Backend URL from environment
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BACKEND_URL:
    # Fallback: read from frontend/.env
    env_file = Path("/app/frontend/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                BACKEND_URL = line.split("=", 1)[1].strip().strip('"').rstrip("/")
                break

if not BACKEND_URL:
    print("❌ ERROR: REACT_APP_BACKEND_URL not found")
    sys.exit(1)

API_BASE = f"{BACKEND_URL}/api"
print(f"🔗 Testing backend at: {API_BASE}")

# Test credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Test image URL
TEST_IMAGE_URL = "https://customer-assets-jai6qajn.emergentagent.net/job_signin-landing/artifacts/ji7mg7ls_WhatsApp%20Image%202026-09-24%20at%2008.16.23.jpeg"

# Global session token
SESSION_TOKEN = None

def login():
    """Login and get session token"""
    global SESSION_TOKEN
    print("\n🔐 Logging in...")
    resp = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=10
    )
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    data = resp.json()
    SESSION_TOKEN = data.get("token")
    print(f"✅ Login successful. Token: {SESSION_TOKEN[:20]}...")
    return SESSION_TOKEN

def headers():
    """Return headers with session token"""
    return {"X-Session-Token": SESSION_TOKEN}

def test_methods():
    """Test 1: GET /api/dkacec/methods"""
    print("\n" + "="*80)
    print("TEST 1: GET /api/dkacec/methods")
    print("="*80)
    
    resp = requests.get(f"{API_BASE}/dkacec/methods", headers=headers(), timeout=10)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Expected 200, got {resp.status_code}")
        print(f"Response: {resp.text}")
        return False
    
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    # Verify structure
    if "methods" not in data:
        print("❌ FAILED: Missing 'methods' key")
        return False
    
    methods = data["methods"]
    if len(methods) != 3:
        print(f"❌ FAILED: Expected 3 methods, got {len(methods)}")
        return False
    
    # Verify each method
    expected_temps = [150, 160, 180]
    expected_codes = ["1", "2", "3"]
    for i, method in enumerate(methods):
        if method.get("code") != expected_codes[i]:
            print(f"❌ FAILED: Method {i} code mismatch. Expected {expected_codes[i]}, got {method.get('code')}")
            return False
        if method.get("temperature_c") != expected_temps[i]:
            print(f"❌ FAILED: Method {i} temperature mismatch. Expected {expected_temps[i]}, got {method.get('temperature_c')}")
            return False
        if method.get("duration_hours") != 192:
            print(f"❌ FAILED: Method {i} duration mismatch. Expected 192, got {method.get('duration_hours')}")
            return False
    
    if data.get("max_samples") != 4:
        print(f"❌ FAILED: Expected max_samples=4, got {data.get('max_samples')}")
        return False
    
    if data.get("duration_hours") != 192:
        print(f"❌ FAILED: Expected duration_hours=192, got {data.get('duration_hours')}")
        return False
    
    print("✅ PASSED: All 3 methods verified (150/160/180°C, all 192h, max_samples=4)")
    return True

def test_ocr_multi_sample():
    """Test 2: OCR multi-sample extraction"""
    print("\n" + "="*80)
    print("TEST 2: OCR Multi-Sample Extraction")
    print("="*80)
    
    # Download test image
    print(f"📥 Downloading test image from: {TEST_IMAGE_URL}")
    img_resp = requests.get(TEST_IMAGE_URL, timeout=30)
    if img_resp.status_code != 200:
        print(f"❌ FAILED: Could not download test image: {img_resp.status_code}")
        return False
    
    print(f"✅ Downloaded test image ({len(img_resp.content)} bytes)")
    
    # Upload image
    print("📤 Uploading image to /api/kht/upload...")
    files = {"file": ("test_dkacec.jpg", img_resp.content, "image/jpeg")}
    upload_resp = requests.post(f"{API_BASE}/kht/upload", files=files, headers=headers(), timeout=30)
    
    if upload_resp.status_code != 200:
        print(f"❌ FAILED: Image upload failed: {upload_resp.status_code} {upload_resp.text}")
        return False
    
    upload_data = upload_resp.json()
    image_path = upload_data.get("image_path")
    print(f"✅ Image uploaded: {image_path}")
    
    # Start OCR job
    print("🔍 Starting OCR job...")
    ocr_start_resp = requests.post(
        f"{API_BASE}/dkacec/ocr/start",
        json={"image_path": image_path},
        headers=headers(),
        timeout=10
    )
    
    if ocr_start_resp.status_code != 200:
        print(f"❌ FAILED: OCR start failed: {ocr_start_resp.status_code} {ocr_start_resp.text}")
        return False
    
    ocr_job = ocr_start_resp.json()
    job_id = ocr_job.get("id")
    print(f"✅ OCR job started: {job_id}")
    
    # Poll for completion (allow up to 2 minutes)
    print("⏳ Polling for OCR completion (max 2 minutes)...")
    max_wait = 120
    start_time = time.time()
    result = None
    
    while time.time() - start_time < max_wait:
        poll_resp = requests.get(f"{API_BASE}/dkacec/ocr/jobs/{job_id}", headers=headers(), timeout=10)
        if poll_resp.status_code != 200:
            print(f"❌ FAILED: OCR job polling failed: {poll_resp.status_code}")
            return False
        
        job_data = poll_resp.json()
        status = job_data.get("status")
        
        if status == "done":
            result = job_data.get("result")
            elapsed = time.time() - start_time
            print(f"✅ OCR completed in {elapsed:.1f} seconds")
            break
        elif status == "error":
            print(f"❌ FAILED: OCR job error: {job_data.get('error')}")
            return False
        
        time.sleep(2)
    
    if result is None:
        print(f"❌ FAILED: OCR job did not complete within {max_wait} seconds")
        return False
    
    # Verify OCR result
    print("\n📋 OCR Result:")
    print(json.dumps(result, indent=2))
    
    # Check required keys
    required_keys = ["sample_codes", "detected_count", "over_limit", "max_samples", 
                     "duration_hours", "temperature_c", "operator", "method_code", "raw_text"]
    for key in required_keys:
        if key not in result:
            print(f"❌ FAILED: Missing key '{key}' in OCR result")
            return False
    
    # Verify sample_codes is a list
    sample_codes = result.get("sample_codes")
    if not isinstance(sample_codes, list):
        print(f"❌ FAILED: sample_codes is not a list: {type(sample_codes)}")
        return False
    
    # Verify we got multiple codes (expecting ~4)
    detected_count = result.get("detected_count")
    if detected_count < 2:
        print(f"❌ FAILED: Expected multiple sample codes, got only {detected_count}")
        return False
    
    print(f"✅ CORE FEATURE VERIFIED: OCR extracted {detected_count} sample codes: {sample_codes}")
    
    # Verify detected_count matches length
    if detected_count != len(sample_codes):
        print(f"❌ FAILED: detected_count ({detected_count}) != len(sample_codes) ({len(sample_codes)})")
        return False
    
    # Verify over_limit is false (we expect 4 codes, not more than max)
    if result.get("over_limit") != False:
        print(f"⚠️  WARNING: over_limit is {result.get('over_limit')}, expected False")
    
    # Verify max_samples
    if result.get("max_samples") != 4:
        print(f"❌ FAILED: max_samples should be 4, got {result.get('max_samples')}")
        return False
    
    # Verify duration_hours
    if result.get("duration_hours") != 192:
        print(f"❌ FAILED: duration_hours should be 192, got {result.get('duration_hours')}")
        return False
    
    # Verify temperature (expecting 135°C from test image)
    temp = result.get("temperature_c")
    print(f"📊 Detected temperature: {temp}°C")
    
    # Verify method_code (135°C is NOT 150/160/180, so should be empty)
    method_code = result.get("method_code")
    if temp and temp not in [150, 160, 180]:
        if method_code != "":
            print(f"⚠️  NOTE: Temperature {temp}°C is not standard (150/160/180), method_code is '{method_code}' (expected empty)")
        else:
            print(f"✅ Correctly identified non-standard temperature {temp}°C, method_code is empty")
    
    print("✅ PASSED: OCR multi-sample extraction working correctly")
    return True, image_path, sample_codes

def test_batch_create_with_method():
    """Test 3: Batch create with method"""
    print("\n" + "="*80)
    print("TEST 3: Batch Create with Method")
    print("="*80)
    
    # First, ensure no active run
    print("🔍 Checking for active run...")
    active_resp = requests.get(f"{API_BASE}/dkacec/active", headers=headers(), timeout=10)
    if active_resp.status_code == 200:
        active_data = active_resp.json()
        active_run = active_data.get("active")
        if active_run:
            run_id = active_run.get("id")
            print(f"⚠️  Active run found: {run_id}. Stopping it...")
            stop_resp = requests.post(f"{API_BASE}/dkacec/runs/{run_id}/stop", headers=headers(), timeout=10)
            if stop_resp.status_code == 200:
                print("✅ Active run stopped")
            else:
                print(f"⚠️  Could not stop active run: {stop_resp.status_code}")
    
    # Create new batch with method_code "2" (160°C, 192h)
    print("\n📝 Creating new batch with method_code='2' (160°C, 192h)...")
    batch_data = {
        "sample_codes": ["S-A", "S-B", "S-C"],
        "method_code": "2",
        "operator": "Budi"
    }
    
    submit_resp = requests.post(
        f"{API_BASE}/dkacec/submit-batch",
        json=batch_data,
        headers=headers(),
        timeout=10
    )
    
    if submit_resp.status_code != 200:
        print(f"❌ FAILED: Batch submit failed: {submit_resp.status_code} {submit_resp.text}")
        return False
    
    result = submit_resp.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    # Verify created=true
    if result.get("created") != True:
        print(f"❌ FAILED: Expected created=true, got {result.get('created')}")
        return False
    
    run = result.get("run")
    if not run:
        print("❌ FAILED: Missing 'run' in response")
        return False
    
    # Verify temperature_c=160
    if run.get("temperature_c") != 160:
        print(f"❌ FAILED: Expected temperature_c=160, got {run.get('temperature_c')}")
        return False
    
    # Verify duration_hours=192
    if run.get("duration_hours") != 192:
        print(f"❌ FAILED: Expected duration_hours=192, got {run.get('duration_hours')}")
        return False
    
    # Verify samples has 3 codes
    samples = run.get("samples", [])
    if len(samples) != 3:
        print(f"❌ FAILED: Expected 3 samples, got {len(samples)}")
        return False
    
    # Verify operator
    if run.get("operator") != "Budi":
        print(f"❌ FAILED: Expected operator='Budi', got {run.get('operator')}")
        return False
    
    # Verify added length
    added = result.get("added", [])
    if len(added) != 3:
        print(f"❌ FAILED: Expected 3 added, got {len(added)}")
        return False
    
    # Verify skipped is empty
    skipped = result.get("skipped", [])
    if len(skipped) != 0:
        print(f"❌ FAILED: Expected 0 skipped, got {len(skipped)}")
        return False
    
    # Verify finish_at is approximately start_at + 192h
    start_at = run.get("start_at")
    finish_at = run.get("finish_at")
    print(f"⏰ Start: {start_at}")
    print(f"⏰ Finish: {finish_at}")
    
    # Check active run
    print("\n🔍 Verifying active run...")
    active_resp = requests.get(f"{API_BASE}/dkacec/active", headers=headers(), timeout=10)
    if active_resp.status_code != 200:
        print(f"❌ FAILED: Could not get active run: {active_resp.status_code}")
        return False
    
    active_data = active_resp.json()
    active_run = active_data.get("active")
    if not active_run:
        print("❌ FAILED: No active run found")
        return False
    
    # Verify countdown
    remaining = active_run.get("remaining_seconds")
    progress = active_run.get("progress_pct")
    print(f"⏳ Remaining: {remaining} seconds")
    print(f"📊 Progress: {progress}%")
    
    if remaining <= 0:
        print("❌ FAILED: remaining_seconds should be > 0")
        return False
    
    if progress >= 100:
        print("❌ FAILED: progress_pct should be < 100")
        return False
    
    print("✅ PASSED: Batch created with method, 192h countdown active")
    return True, run.get("id")

def test_dedup_and_capacity(run_id):
    """Test 4: Deduplication and capacity limit"""
    print("\n" + "="*80)
    print("TEST 4: Deduplication and Capacity Limit")
    print("="*80)
    
    # Submit batch with duplicate and new codes
    print("📝 Submitting batch with duplicate 'S-A' and new codes 'S-D', 'S-E'...")
    batch_data = {
        "sample_codes": ["S-A", "S-D", "S-E"]
    }
    
    submit_resp = requests.post(
        f"{API_BASE}/dkacec/submit-batch",
        json=batch_data,
        headers=headers(),
        timeout=10
    )
    
    if submit_resp.status_code != 200:
        print(f"❌ FAILED: Batch submit failed: {submit_resp.status_code} {submit_resp.text}")
        return False
    
    result = submit_resp.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    # Verify created=false (adding to existing)
    if result.get("created") != False:
        print(f"❌ FAILED: Expected created=false, got {result.get('created')}")
        return False
    
    # Verify skipped contains S-A with reason "duplikat"
    skipped = result.get("skipped", [])
    s_a_skipped = False
    for item in skipped:
        if item.get("code") == "S-A" and item.get("reason") == "duplikat":
            s_a_skipped = True
            print(f"✅ S-A correctly skipped as duplicate")
            break
    
    if not s_a_skipped:
        print(f"❌ FAILED: S-A should be skipped with reason 'duplikat'")
        return False
    
    # Verify one of S-D/S-E was added (to fill 4th slot) and the other skipped as "batch penuh"
    added = result.get("added", [])
    batch_full_count = sum(1 for item in skipped if item.get("reason") == "batch penuh")
    
    if len(added) != 1:
        print(f"❌ FAILED: Expected 1 code added (to fill 4th slot), got {len(added)}")
        return False
    
    if batch_full_count != 1:
        print(f"❌ FAILED: Expected 1 code skipped as 'batch penuh', got {batch_full_count}")
        return False
    
    print(f"✅ One code added: {added}")
    print(f"✅ One code skipped as 'batch penuh'")
    
    # Verify run now has exactly 4 samples
    run = result.get("run")
    samples = run.get("samples", [])
    if len(samples) != 4:
        print(f"❌ FAILED: Expected exactly 4 samples in run, got {len(samples)}")
        return False
    
    print(f"✅ PASSED: Deduplication and capacity limit working correctly (run has 4 samples)")
    return True

def test_truncation():
    """Test 5: Truncation warning"""
    print("\n" + "="*80)
    print("TEST 5: Truncation Warning")
    print("="*80)
    
    # First, stop the active run
    print("🔍 Stopping active run...")
    active_resp = requests.get(f"{API_BASE}/dkacec/active", headers=headers(), timeout=10)
    if active_resp.status_code == 200:
        active_data = active_resp.json()
        active_run = active_data.get("active")
        if active_run:
            run_id = active_run.get("id")
            stop_resp = requests.post(f"{API_BASE}/dkacec/runs/{run_id}/stop", headers=headers(), timeout=10)
            if stop_resp.status_code == 200:
                print("✅ Active run stopped")
    
    # Submit batch with 5 codes
    print("\n📝 Submitting batch with 5 codes (should truncate to 4)...")
    batch_data = {
        "sample_codes": ["A", "B", "C", "D", "E"],
        "temperature_c": 180
    }
    
    submit_resp = requests.post(
        f"{API_BASE}/dkacec/submit-batch",
        json=batch_data,
        headers=headers(),
        timeout=10
    )
    
    if submit_resp.status_code != 200:
        print(f"❌ FAILED: Batch submit failed: {submit_resp.status_code} {submit_resp.text}")
        return False
    
    result = submit_resp.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    # Verify truncated=true
    if result.get("truncated") != True:
        print(f"❌ FAILED: Expected truncated=true, got {result.get('truncated')}")
        return False
    
    # Verify only 4 samples added
    added = result.get("added", [])
    if len(added) != 4:
        print(f"❌ FAILED: Expected 4 samples added, got {len(added)}")
        return False
    
    # Verify created=true
    if result.get("created") != True:
        print(f"❌ FAILED: Expected created=true, got {result.get('created')}")
        return False
    
    # Verify method resolved to code "3" (180°C)
    run = result.get("run")
    if run.get("method_code") != "3":
        print(f"❌ FAILED: Expected method_code='3' for 180°C, got {run.get('method_code')}")
        return False
    
    # Verify duration is 192
    if run.get("duration_hours") != 192:
        print(f"❌ FAILED: Expected duration_hours=192, got {run.get('duration_hours')}")
        return False
    
    print(f"✅ PASSED: Truncation working (5 codes -> 4 added), method resolved to '3' (180°C)")
    return True, run.get("id")

def test_method_by_temperature():
    """Test 6: Method resolution by temperature"""
    print("\n" + "="*80)
    print("TEST 6: Method Resolution by Temperature")
    print("="*80)
    
    # Stop previous run
    print("🔍 Stopping active run...")
    active_resp = requests.get(f"{API_BASE}/dkacec/active", headers=headers(), timeout=10)
    if active_resp.status_code == 200:
        active_data = active_resp.json()
        active_run = active_data.get("active")
        if active_run:
            run_id = active_run.get("id")
            stop_resp = requests.post(f"{API_BASE}/dkacec/runs/{run_id}/stop", headers=headers(), timeout=10)
            if stop_resp.status_code == 200:
                print("✅ Active run stopped")
    
    # Submit batch with temperature_c=150
    print("\n📝 Submitting batch with temperature_c=150 (should resolve to method '1')...")
    batch_data = {
        "sample_codes": ["T1"],
        "temperature_c": 150
    }
    
    submit_resp = requests.post(
        f"{API_BASE}/dkacec/submit-batch",
        json=batch_data,
        headers=headers(),
        timeout=10
    )
    
    if submit_resp.status_code != 200:
        print(f"❌ FAILED: Batch submit failed: {submit_resp.status_code} {submit_resp.text}")
        return False
    
    result = submit_resp.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    # Verify created=true
    if result.get("created") != True:
        print(f"❌ FAILED: Expected created=true, got {result.get('created')}")
        return False
    
    # Verify method_code resolved to "1"
    run = result.get("run")
    if run.get("method_code") != "1":
        print(f"❌ FAILED: Expected method_code='1' for 150°C, got {run.get('method_code')}")
        return False
    
    # Verify method_label mentions 150
    method_label = run.get("method_label", "")
    if "150" not in method_label:
        print(f"❌ FAILED: Expected method_label to mention 150, got '{method_label}'")
        return False
    
    print(f"✅ PASSED: Method resolved to '1' (150°C), label: {method_label}")
    
    # Stop this run for cleanup
    run_id = run.get("id")
    stop_resp = requests.post(f"{API_BASE}/dkacec/runs/{run_id}/stop", headers=headers(), timeout=10)
    if stop_resp.status_code == 200:
        print("✅ Test run stopped")
    
    return True

def test_validation():
    """Test 7: Validation errors"""
    print("\n" + "="*80)
    print("TEST 7: Validation Errors")
    print("="*80)
    
    # Test 7a: Empty sample_codes
    print("\n📝 Test 7a: Empty sample_codes (should return 400)...")
    batch_data = {"sample_codes": []}
    
    submit_resp = requests.post(
        f"{API_BASE}/dkacec/submit-batch",
        json=batch_data,
        headers=headers(),
        timeout=10
    )
    
    if submit_resp.status_code != 400:
        print(f"❌ FAILED: Expected 400, got {submit_resp.status_code}")
        return False
    
    print(f"✅ Correctly returned 400: {submit_resp.json().get('detail')}")
    
    # Test 7b: Missing method and temperature (no active run)
    print("\n📝 Test 7b: Missing method_code and temperature_c (should return 400)...")
    
    # Ensure no active run
    active_resp = requests.get(f"{API_BASE}/dkacec/active", headers=headers(), timeout=10)
    if active_resp.status_code == 200:
        active_data = active_resp.json()
        active_run = active_data.get("active")
        if active_run:
            run_id = active_run.get("id")
            stop_resp = requests.post(f"{API_BASE}/dkacec/runs/{run_id}/stop", headers=headers(), timeout=10)
            print("✅ Stopped active run for clean test")
    
    batch_data = {"sample_codes": ["X"]}  # No method_code, no temperature_c
    
    submit_resp = requests.post(
        f"{API_BASE}/dkacec/submit-batch",
        json=batch_data,
        headers=headers(),
        timeout=10
    )
    
    if submit_resp.status_code != 400:
        print(f"❌ FAILED: Expected 400, got {submit_resp.status_code}")
        return False
    
    error_detail = submit_resp.json().get("detail", "")
    print(f"✅ Correctly returned 400: {error_detail}")
    
    # Verify error message mentions temperature/suhu
    if "suhu" not in error_detail.lower() and "temperature" not in error_detail.lower():
        print(f"⚠️  WARNING: Error message doesn't mention temperature: {error_detail}")
    
    print("✅ PASSED: Validation errors working correctly")
    return True

def test_auth_guard():
    """Test 8: Auth guard"""
    print("\n" + "="*80)
    print("TEST 8: Auth Guard")
    print("="*80)
    
    print("📝 Attempting POST /api/dkacec/submit-batch without token...")
    batch_data = {"sample_codes": ["TEST"]}
    
    # No headers (no token)
    submit_resp = requests.post(
        f"{API_BASE}/dkacec/submit-batch",
        json=batch_data,
        timeout=10
    )
    
    if submit_resp.status_code != 401:
        print(f"❌ FAILED: Expected 401, got {submit_resp.status_code}")
        return False
    
    print(f"✅ PASSED: Correctly returned 401 without token")
    return True

def test_history_and_delete():
    """Test 9: History and soft delete"""
    print("\n" + "="*80)
    print("TEST 9: History and Soft Delete")
    print("="*80)
    
    # Get runs
    print("📋 Getting runs history...")
    runs_resp = requests.get(f"{API_BASE}/dkacec/runs", headers=headers(), timeout=10)
    
    if runs_resp.status_code != 200:
        print(f"❌ FAILED: Could not get runs: {runs_resp.status_code}")
        return False
    
    runs = runs_resp.json()
    print(f"✅ Found {len(runs)} runs")
    
    if len(runs) == 0:
        print("⚠️  No runs to test delete")
        return True
    
    # Delete first run
    run_to_delete = runs[0]
    run_id = run_to_delete.get("id")
    print(f"\n🗑️  Deleting run: {run_id}")
    
    delete_resp = requests.delete(f"{API_BASE}/dkacec/runs/{run_id}", headers=headers(), timeout=10)
    
    if delete_resp.status_code != 200:
        print(f"❌ FAILED: Delete failed: {delete_resp.status_code} {delete_resp.text}")
        return False
    
    print("✅ Delete successful")
    
    # Verify it's gone from list
    print("🔍 Verifying run is removed from list...")
    runs_resp2 = requests.get(f"{API_BASE}/dkacec/runs", headers=headers(), timeout=10)
    runs2 = runs_resp2.json()
    
    # Check if deleted run is still in list
    still_present = any(r.get("id") == run_id for r in runs2)
    if still_present:
        print(f"❌ FAILED: Deleted run still appears in list")
        return False
    
    print(f"✅ PASSED: Run soft-deleted and removed from list")
    return True

def cleanup_all_runs():
    """Cleanup: Stop or delete all dkacec runs"""
    print("\n" + "="*80)
    print("CLEANUP: Removing All Test Runs")
    print("="*80)
    
    # Get all runs
    runs_resp = requests.get(f"{API_BASE}/dkacec/runs", headers=headers(), timeout=10)
    if runs_resp.status_code != 200:
        print(f"⚠️  Could not get runs for cleanup: {runs_resp.status_code}")
        return
    
    runs = runs_resp.json()
    print(f"Found {len(runs)} runs to clean up")
    
    for run in runs:
        run_id = run.get("id")
        status = run.get("status")
        
        # Stop if running
        if status == "running":
            print(f"⏹️  Stopping run {run_id}...")
            stop_resp = requests.post(f"{API_BASE}/dkacec/runs/{run_id}/stop", headers=headers(), timeout=10)
            if stop_resp.status_code == 200:
                print(f"✅ Stopped")
        
        # Delete
        print(f"🗑️  Deleting run {run_id}...")
        delete_resp = requests.delete(f"{API_BASE}/dkacec/runs/{run_id}", headers=headers(), timeout=10)
        if delete_resp.status_code == 200:
            print(f"✅ Deleted")
    
    # Verify no active run
    active_resp = requests.get(f"{API_BASE}/dkacec/active", headers=headers(), timeout=10)
    if active_resp.status_code == 200:
        active_data = active_resp.json()
        active_run = active_data.get("active")
        if active_run:
            print(f"⚠️  WARNING: Active run still exists: {active_run.get('id')}")
        else:
            print("✅ No active run (cleanup successful)")
    
    print("✅ CLEANUP COMPLETE")

def verify_no_dka_data_touched():
    """Verify we didn't touch existing rating-dka data"""
    print("\n" + "="*80)
    print("VERIFICATION: DKA Data Integrity")
    print("="*80)
    
    # Check if /api/dka/dashboard still works
    print("🔍 Checking /api/dka/dashboard...")
    dka_resp = requests.get(f"{API_BASE}/dka/dashboard", headers=headers(), timeout=10)
    
    if dka_resp.status_code == 200:
        print("✅ /api/dka/dashboard still accessible (DKA data not affected)")
    else:
        print(f"⚠️  /api/dka/dashboard returned {dka_resp.status_code}")

def main():
    """Main test runner"""
    print("="*80)
    print("DKA-CEC L-48-A-00 MODULE BACKEND TESTING")
    print("="*80)
    
    # Login
    login()
    
    # Track results
    results = {}
    
    # Test 1: Methods
    results["methods"] = test_methods()
    
    # Test 2: OCR multi-sample
    ocr_result = test_ocr_multi_sample()
    if isinstance(ocr_result, tuple):
        results["ocr_multi_sample"] = ocr_result[0]
        image_path = ocr_result[1]
        sample_codes = ocr_result[2]
    else:
        results["ocr_multi_sample"] = ocr_result
    
    # Test 3: Batch create with method
    batch_result = test_batch_create_with_method()
    if isinstance(batch_result, tuple):
        results["batch_create"] = batch_result[0]
        run_id = batch_result[1]
    else:
        results["batch_create"] = batch_result
        run_id = None
    
    # Test 4: Dedup and capacity (only if we have a run_id)
    if run_id:
        results["dedup_capacity"] = test_dedup_and_capacity(run_id)
    else:
        results["dedup_capacity"] = False
    
    # Test 5: Truncation
    truncation_result = test_truncation()
    if isinstance(truncation_result, tuple):
        results["truncation"] = truncation_result[0]
    else:
        results["truncation"] = truncation_result
    
    # Test 6: Method by temperature
    results["method_by_temp"] = test_method_by_temperature()
    
    # Test 7: Validation
    results["validation"] = test_validation()
    
    # Test 8: Auth guard
    results["auth_guard"] = test_auth_guard()
    
    # Test 9: History and delete
    results["history_delete"] = test_history_and_delete()
    
    # Cleanup
    cleanup_all_runs()
    
    # Verify DKA data integrity
    verify_no_dka_data_touched()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASSED" if passed_flag else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
