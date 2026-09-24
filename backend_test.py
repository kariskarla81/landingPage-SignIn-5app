#!/usr/bin/env python3
"""
Backend test for HTCBT multi-sample batch OCR (ASTM D6594)
Tests the NEW multi-sample batch OCR feature ONLY.
"""

import requests
import time
import json
import sys
from typing import Optional

# Backend URL from frontend/.env
BASE_URL = "https://signin-landing.preview.emergentagent.com/api"

# Test credentials
USERNAME = "admin"
PASSWORD = "admin123"

# Test image URL (handwritten note with 4 samples)
TEST_IMAGE_URL = "https://customer-assets-jai6qajn.emergentagent.net/job_signin-landing/artifacts/ji7mg7ls_WhatsApp%20Image%202026-09-24%20at%2008.16.23.jpeg"

# Expected OCR results (allow minor variance)
EXPECTED_SAMPLES = ["WZ 275215", "BL 275314", "NT 265142", "WZ 265336"]
EXPECTED_DURATION = 168
EXPECTED_TEMP = 135
EXPECTED_METHOD = "A"

# Global session token
session_token: Optional[str] = None


def log(msg: str):
    """Print test log message"""
    print(f"[TEST] {msg}")


def log_error(msg: str):
    """Print error message"""
    print(f"[ERROR] {msg}", file=sys.stderr)


def login() -> str:
    """Login and return session token"""
    log("Logging in...")
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=10
    )
    if resp.status_code != 200:
        log_error(f"Login failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    data = resp.json()
    token = data.get("token")
    if not token:
        log_error(f"No token in login response: {data}")
        sys.exit(1)
    
    log(f"✅ Login successful. Token: {token[:20]}...")
    return token


def get_headers(with_auth: bool = True) -> dict:
    """Get request headers with optional auth token"""
    headers = {"Content-Type": "application/json"}
    if with_auth and session_token:
        headers["X-Session-Token"] = session_token
    return headers


def download_test_image() -> bytes:
    """Download test image from URL"""
    log(f"Downloading test image from {TEST_IMAGE_URL}...")
    resp = requests.get(TEST_IMAGE_URL, timeout=30)
    if resp.status_code != 200:
        log_error(f"Failed to download test image: {resp.status_code}")
        sys.exit(1)
    log(f"✅ Downloaded test image ({len(resp.content)} bytes)")
    return resp.content


def upload_image(image_data: bytes) -> str:
    """Upload image via POST /api/kht/upload and return path"""
    log("Uploading image to /api/kht/upload...")
    files = {"file": ("test_htcbt.jpg", image_data, "image/jpeg")}
    headers = {"X-Session-Token": session_token} if session_token else {}
    
    resp = requests.post(
        f"{BASE_URL}/kht/upload",
        files=files,
        headers=headers,
        timeout=30
    )
    
    if resp.status_code != 200:
        log_error(f"Image upload failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    data = resp.json()
    image_path = data.get("image_path") or data.get("path")
    if not image_path:
        log_error(f"No path in upload response: {data}")
        sys.exit(1)
    
    log(f"✅ Image uploaded: {image_path}")
    return image_path


def start_ocr_job(image_path: str) -> str:
    """Start OCR job and return job ID"""
    log("Starting OCR job...")
    resp = requests.post(
        f"{BASE_URL}/htcbt/ocr/start",
        json={"image_path": image_path},
        headers=get_headers(),
        timeout=10
    )
    
    if resp.status_code != 200:
        log_error(f"OCR start failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    data = resp.json()
    job_id = data.get("id")
    status = data.get("status")
    
    if not job_id:
        log_error(f"No job ID in response: {data}")
        sys.exit(1)
    
    log(f"✅ OCR job started: {job_id} (status: {status})")
    return job_id


def poll_ocr_job(job_id: str, max_wait: int = 120) -> dict:
    """Poll OCR job until done or timeout"""
    log(f"Polling OCR job {job_id} (max {max_wait}s)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        resp = requests.get(
            f"{BASE_URL}/htcbt/ocr/jobs/{job_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if resp.status_code != 200:
            log_error(f"Job polling failed: {resp.status_code} {resp.text}")
            sys.exit(1)
        
        data = resp.json()
        status = data.get("status")
        
        if status == "done":
            elapsed = time.time() - start_time
            log(f"✅ OCR job completed in {elapsed:.1f}s")
            return data
        elif status == "error":
            error = data.get("error", "Unknown error")
            log_error(f"OCR job failed: {error}")
            sys.exit(1)
        
        time.sleep(2)
    
    log_error(f"OCR job timeout after {max_wait}s")
    sys.exit(1)


def verify_ocr_result(job_data: dict):
    """Verify OCR result contains expected fields and values"""
    log("Verifying OCR result...")
    result = job_data.get("result")
    
    if not result:
        log_error(f"No result in job data: {job_data}")
        sys.exit(1)
    
    # Check required fields
    required_fields = [
        "sample_codes", "sample_code", "detected_count", "over_limit",
        "max_samples", "temperature_c", "duration_hours", "method_code", "raw_text"
    ]
    
    for field in required_fields:
        if field not in result:
            log_error(f"Missing field '{field}' in OCR result")
            sys.exit(1)
    
    # Verify sample_codes is a list
    sample_codes = result.get("sample_codes")
    if not isinstance(sample_codes, list):
        log_error(f"sample_codes is not a list: {type(sample_codes)}")
        sys.exit(1)
    
    # Verify detected_count matches list length
    detected_count = result.get("detected_count")
    if detected_count != len(sample_codes):
        log_error(f"detected_count ({detected_count}) != len(sample_codes) ({len(sample_codes)})")
        sys.exit(1)
    
    # Verify max_samples is 4
    max_samples = result.get("max_samples")
    if max_samples != 4:
        log_error(f"max_samples should be 4, got {max_samples}")
        sys.exit(1)
    
    # Verify over_limit is false (we expect 4 samples)
    over_limit = result.get("over_limit")
    if over_limit:
        log_error(f"over_limit should be false, got {over_limit}")
        sys.exit(1)
    
    # Verify sample_code (first code, back-compat)
    sample_code = result.get("sample_code")
    if sample_code != sample_codes[0]:
        log_error(f"sample_code ({sample_code}) != sample_codes[0] ({sample_codes[0]})")
        sys.exit(1)
    
    # Verify temperature and duration (allow some variance)
    temperature_c = result.get("temperature_c")
    duration_hours = result.get("duration_hours")
    
    if temperature_c is None or abs(temperature_c - EXPECTED_TEMP) > 10:
        log_error(f"temperature_c ({temperature_c}) not close to expected {EXPECTED_TEMP}")
        sys.exit(1)
    
    if duration_hours is None or abs(duration_hours - EXPECTED_DURATION) > 24:
        log_error(f"duration_hours ({duration_hours}) not close to expected {EXPECTED_DURATION}")
        sys.exit(1)
    
    # Verify method_code
    method_code = result.get("method_code")
    if method_code != EXPECTED_METHOD:
        log_error(f"method_code ({method_code}) != expected {EXPECTED_METHOD}")
        sys.exit(1)
    
    # Verify we got multiple samples (the CORE feature)
    if len(sample_codes) < 2:
        log_error(f"Expected multiple samples, got only {len(sample_codes)}: {sample_codes}")
        sys.exit(1)
    
    log(f"✅ OCR result verified:")
    log(f"   - sample_codes: {sample_codes}")
    log(f"   - detected_count: {detected_count}")
    log(f"   - temperature_c: {temperature_c}")
    log(f"   - duration_hours: {duration_hours}")
    log(f"   - method_code: {method_code}")
    log(f"   - over_limit: {over_limit}")
    log(f"   - max_samples: {max_samples}")
    
    return result


def get_active_run() -> Optional[dict]:
    """Get active HTCBT run"""
    resp = requests.get(
        f"{BASE_URL}/htcbt/active",
        headers=get_headers(),
        timeout=10
    )
    
    if resp.status_code != 200:
        log_error(f"Failed to get active run: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    data = resp.json()
    return data.get("active")


def stop_run(run_id: str):
    """Stop a running HTCBT run"""
    log(f"Stopping run {run_id}...")
    resp = requests.post(
        f"{BASE_URL}/htcbt/runs/{run_id}/stop",
        headers=get_headers(),
        timeout=10
    )
    
    if resp.status_code != 200:
        log_error(f"Failed to stop run: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    log(f"✅ Run stopped: {run_id}")


def delete_run(run_id: str):
    """Delete a HTCBT run"""
    log(f"Deleting run {run_id}...")
    resp = requests.delete(
        f"{BASE_URL}/htcbt/runs/{run_id}",
        headers=get_headers(),
        timeout=10
    )
    
    if resp.status_code != 200:
        log_error(f"Failed to delete run: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    log(f"✅ Run deleted: {run_id}")


def submit_batch(sample_codes: list, duration_hours: float, temperature_c: float, 
                 method_code: str, operator: str = "Test Operator",
                 image_path: str = "", ocr_raw: str = "") -> dict:
    """Submit batch of samples"""
    log(f"Submitting batch: {sample_codes}")
    resp = requests.post(
        f"{BASE_URL}/htcbt/submit-batch",
        json={
            "sample_codes": sample_codes,
            "duration_hours": duration_hours,
            "temperature_c": temperature_c,
            "method_code": method_code,
            "operator": operator,
            "image_path": image_path,
            "ocr_raw": ocr_raw
        },
        headers=get_headers(),
        timeout=10
    )
    
    if resp.status_code not in [200, 400, 401, 409]:
        log_error(f"Batch submit failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else None, "text": resp.text}


def test_ocr_flow():
    """Test 1: OCR reads multiple samples"""
    log("\n=== TEST 1: OCR READS MULTIPLE SAMPLES ===")
    
    # Download and upload test image
    image_data = download_test_image()
    image_path = upload_image(image_data)
    
    # Start OCR job
    job_id = start_ocr_job(image_path)
    
    # Poll until done
    job_data = poll_ocr_job(job_id)
    
    # Verify result
    result = verify_ocr_result(job_data)
    
    log("✅ TEST 1 PASSED: OCR successfully reads multiple samples")
    return result, image_path


def test_batch_create(sample_codes: list, duration_hours: float, temperature_c: float, 
                      method_code: str, image_path: str, ocr_raw: str):
    """Test 2: Batch create with multiple samples"""
    log("\n=== TEST 2: BATCH CREATE ===")
    
    # Ensure no active run
    active = get_active_run()
    if active:
        log(f"Active run exists: {active['id']}, stopping it first...")
        stop_run(active["id"])
    
    # Submit batch
    result = submit_batch(sample_codes, duration_hours, temperature_c, method_code, 
                         image_path=image_path, ocr_raw=ocr_raw)
    
    if result["status_code"] != 200:
        log_error(f"Batch create failed: {result['status_code']} {result['text']}")
        sys.exit(1)
    
    data = result["data"]
    
    # Verify response
    if not data.get("created"):
        log_error(f"created should be true, got {data.get('created')}")
        sys.exit(1)
    
    run = data.get("run")
    if not run:
        log_error("No run in response")
        sys.exit(1)
    
    samples = run.get("samples", [])
    if len(samples) != len(sample_codes):
        log_error(f"Expected {len(sample_codes)} samples, got {len(samples)}")
        sys.exit(1)
    
    added = data.get("added", [])
    if len(added) != len(sample_codes):
        log_error(f"Expected {len(sample_codes)} added, got {len(added)}")
        sys.exit(1)
    
    skipped = data.get("skipped", [])
    if len(skipped) != 0:
        log_error(f"Expected 0 skipped, got {len(skipped)}")
        sys.exit(1)
    
    truncated = data.get("truncated")
    if truncated:
        log_error(f"truncated should be false, got {truncated}")
        sys.exit(1)
    
    log(f"✅ Batch created: run_id={run['id']}, samples={len(samples)}")
    log(f"   - added: {added}")
    log(f"   - skipped: {skipped}")
    log(f"   - truncated: {truncated}")
    
    # Verify active run
    active = get_active_run()
    if not active:
        log_error("No active run after batch create")
        sys.exit(1)
    
    if active["id"] != run["id"]:
        log_error(f"Active run ID mismatch: {active['id']} != {run['id']}")
        sys.exit(1)
    
    if len(active["samples"]) != len(sample_codes):
        log_error(f"Active run has {len(active['samples'])} samples, expected {len(sample_codes)}")
        sys.exit(1)
    
    log("✅ TEST 2 PASSED: Batch create successful")
    return run["id"]


def test_dedup_and_capacity(run_id: str):
    """Test 3: Deduplication and capacity limit"""
    log("\n=== TEST 3: DEDUP + CAPACITY ===")
    
    # Submit batch with one duplicate and one new sample
    # The run already has 4 samples, so both should be skipped
    sample_codes = ["WZ 275215", "EX-NEW-1"]  # First is duplicate, second is new but batch full
    
    result = submit_batch(sample_codes, 168, 135, "A")
    
    if result["status_code"] != 200:
        log_error(f"Batch submit failed: {result['status_code']} {result['text']}")
        sys.exit(1)
    
    data = result["data"]
    
    # Verify response
    if data.get("created"):
        log_error(f"created should be false (adding to existing run), got {data.get('created')}")
        sys.exit(1)
    
    added = data.get("added", [])
    skipped = data.get("skipped", [])
    
    # Both should be skipped (one duplicate, one over capacity)
    if len(added) != 0:
        log_error(f"Expected 0 added (batch full), got {len(added)}: {added}")
        sys.exit(1)
    
    if len(skipped) != 2:
        log_error(f"Expected 2 skipped, got {len(skipped)}: {skipped}")
        sys.exit(1)
    
    # Verify skip reasons
    skip_reasons = {s["code"]: s["reason"] for s in skipped}
    
    if "WZ 275215" not in skip_reasons:
        log_error(f"Expected 'WZ 275215' in skipped")
        sys.exit(1)
    
    if skip_reasons["WZ 275215"] != "duplikat":
        log_error(f"Expected reason 'duplikat' for WZ 275215, got {skip_reasons['WZ 275215']}")
        sys.exit(1)
    
    if "EX-NEW-1" not in skip_reasons:
        log_error(f"Expected 'EX-NEW-1' in skipped")
        sys.exit(1)
    
    if skip_reasons["EX-NEW-1"] != "batch penuh":
        log_error(f"Expected reason 'batch penuh' for EX-NEW-1, got {skip_reasons['EX-NEW-1']}")
        sys.exit(1)
    
    # Verify run still has only 4 samples
    run = data.get("run")
    if len(run["samples"]) != 4:
        log_error(f"Run should still have 4 samples, got {len(run['samples'])}")
        sys.exit(1)
    
    log(f"✅ Dedup and capacity verified:")
    log(f"   - added: {added}")
    log(f"   - skipped: {skipped}")
    log(f"   - run still has 4 samples")
    
    log("✅ TEST 3 PASSED: Dedup and capacity limit working")


def test_truncation():
    """Test 4: Truncation warning when submitting >4 samples"""
    log("\n=== TEST 4: TRUNCATION WARNING ===")
    
    # Stop/delete active run first
    active = get_active_run()
    if active:
        log(f"Stopping active run {active['id']}...")
        stop_run(active["id"])
    
    # Submit 5 samples (should truncate to 4)
    sample_codes = ["S1", "S2", "S3", "S4", "S5"]
    
    result = submit_batch(sample_codes, 168, 135, "A")
    
    if result["status_code"] != 200:
        log_error(f"Batch submit failed: {result['status_code']} {result['text']}")
        sys.exit(1)
    
    data = result["data"]
    
    # Verify truncated flag
    truncated = data.get("truncated")
    if not truncated:
        log_error(f"truncated should be true, got {truncated}")
        sys.exit(1)
    
    # Verify only 4 samples added
    added = data.get("added", [])
    if len(added) != 4:
        log_error(f"Expected 4 added (truncated), got {len(added)}: {added}")
        sys.exit(1)
    
    # Verify S5 was dropped
    if "S5" in added:
        log_error(f"S5 should have been dropped, but it's in added: {added}")
        sys.exit(1)
    
    # Verify run has only 4 samples
    run = data.get("run")
    if len(run["samples"]) != 4:
        log_error(f"Run should have 4 samples, got {len(run['samples'])}")
        sys.exit(1)
    
    log(f"✅ Truncation verified:")
    log(f"   - truncated: {truncated}")
    log(f"   - added: {added} (S5 dropped)")
    log(f"   - run has 4 samples")
    
    log("✅ TEST 4 PASSED: Truncation warning working")
    return run["id"]


def test_validation():
    """Test 5: Validation errors"""
    log("\n=== TEST 5: VALIDATION ===")
    
    # Stop/delete active run first
    active = get_active_run()
    if active:
        log(f"Stopping active run {active['id']}...")
        stop_run(active["id"])
    
    # Test 5a: Empty sample_codes
    log("Testing empty sample_codes...")
    result = submit_batch([], 168, 135, "A")
    
    if result["status_code"] != 400:
        log_error(f"Expected 400 for empty sample_codes, got {result['status_code']}")
        sys.exit(1)
    
    log("✅ Empty sample_codes correctly rejected (400)")
    
    # Test 5b: Missing duration and method_code (and no temperature to infer from)
    log("Testing missing duration and method_code...")
    result = submit_batch(["TEST1"], None, None, None)
    
    if result["status_code"] != 400:
        log_error(f"Expected 400 for missing duration, got {result['status_code']}")
        sys.exit(1)
    
    if "durasi" not in result["text"].lower():
        log_error(f"Expected 'durasi' in error message, got: {result['text']}")
        sys.exit(1)
    
    log("✅ Missing duration correctly rejected (400)")
    
    log("✅ TEST 5 PASSED: Validation working")


def test_auth_guard():
    """Test 6: Auth guard"""
    log("\n=== TEST 6: AUTH GUARD ===")
    
    # Try to submit batch without token
    log("Testing submit-batch without token...")
    resp = requests.post(
        f"{BASE_URL}/htcbt/submit-batch",
        json={
            "sample_codes": ["TEST1"],
            "duration_hours": 168,
            "temperature_c": 135,
            "method_code": "A"
        },
        headers={"Content-Type": "application/json"},  # No auth token
        timeout=10
    )
    
    if resp.status_code != 401:
        log_error(f"Expected 401 without token, got {resp.status_code}")
        sys.exit(1)
    
    log("✅ Auth guard working (401 without token)")
    
    log("✅ TEST 6 PASSED: Auth guard working")


def cleanup():
    """Cleanup: stop/delete any active runs"""
    log("\n=== CLEANUP ===")
    
    active = get_active_run()
    if active:
        log(f"Cleaning up active run {active['id']}...")
        stop_run(active["id"])
        delete_run(active["id"])
    
    log("✅ Cleanup complete")


def main():
    """Main test runner"""
    global session_token
    
    log("=" * 60)
    log("HTCBT MULTI-SAMPLE BATCH OCR BACKEND TEST")
    log("=" * 60)
    
    try:
        # Login
        session_token = login()
        
        # Test 1: OCR flow
        ocr_result, image_path = test_ocr_flow()
        sample_codes = ocr_result["sample_codes"]
        duration_hours = ocr_result["duration_hours"]
        temperature_c = ocr_result["temperature_c"]
        method_code = ocr_result["method_code"]
        ocr_raw = ocr_result["raw_text"]
        
        # Test 2: Batch create
        run_id = test_batch_create(sample_codes, duration_hours, temperature_c, 
                                   method_code, image_path, ocr_raw)
        
        # Test 3: Dedup and capacity
        test_dedup_and_capacity(run_id)
        
        # Test 4: Truncation
        run_id = test_truncation()
        
        # Test 5: Validation
        test_validation()
        
        # Test 6: Auth guard
        test_auth_guard()
        
        # Cleanup
        cleanup()
        
        log("\n" + "=" * 60)
        log("✅ ALL TESTS PASSED")
        log("=" * 60)
        
    except KeyboardInterrupt:
        log("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
