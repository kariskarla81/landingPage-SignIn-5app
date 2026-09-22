#!/usr/bin/env python3
"""
Backend Auth Testing Script
Tests the authentication flow for the Elastech Production API
"""
import os
import sys
import requests
import json
from typing import Optional

# Load backend URL from frontend/.env
FRONTEND_ENV_PATH = "/app/frontend/.env"
BACKEND_URL = None

try:
    with open(FRONTEND_ENV_PATH, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.split('=', 1)[1].strip()
                break
except Exception as e:
    print(f"❌ Failed to read frontend/.env: {e}")
    sys.exit(1)

if not BACKEND_URL:
    print("❌ REACT_APP_BACKEND_URL not found in frontend/.env")
    sys.exit(1)

BASE_URL = f"{BACKEND_URL}/api"
print(f"🔗 Testing against: {BASE_URL}")
print("=" * 80)

# Test credentials from /app/memory/test_credentials.md
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
OLD_PASSWORD = "Elastech@2026"

# Test results tracking
tests_passed = 0
tests_failed = 0
test_results = []

def log_test(name: str, passed: bool, details: str = ""):
    global tests_passed, tests_failed
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   {details}")
    test_results.append({"name": name, "passed": passed, "details": details})
    if passed:
        tests_passed += 1
    else:
        tests_failed += 1

def test_login_correct_credentials() -> Optional[str]:
    """Test 1: POST /api/auth/login with correct credentials"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "username" in data and "ttl_minutes" in data:
                if data["username"] == ADMIN_USERNAME and data["ttl_minutes"] == 60:
                    log_test(
                        "Login with correct credentials (admin/admin123)",
                        True,
                        f"Got token, username={data['username']}, ttl_minutes={data['ttl_minutes']}"
                    )
                    return data["token"]
                else:
                    log_test(
                        "Login with correct credentials (admin/admin123)",
                        False,
                        f"Response structure incorrect: {data}"
                    )
            else:
                log_test(
                    "Login with correct credentials (admin/admin123)",
                    False,
                    f"Missing required fields in response: {data}"
                )
        else:
            log_test(
                "Login with correct credentials (admin/admin123)",
                False,
                f"Expected 200, got {response.status_code}: {response.text}"
            )
    except Exception as e:
        log_test("Login with correct credentials (admin/admin123)", False, f"Exception: {e}")
    return None

def test_login_wrong_password():
    """Test 2: POST /api/auth/login with wrong password"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": ADMIN_USERNAME, "password": "wrongpass"},
            timeout=10
        )
        
        if response.status_code == 401:
            data = response.json()
            if "detail" in data and data["detail"] == "Username atau password salah":
                log_test(
                    "Login with wrong password",
                    True,
                    f"Got expected 401 with message: {data['detail']}"
                )
            else:
                log_test(
                    "Login with wrong password",
                    False,
                    f"Got 401 but wrong message: {data}"
                )
        else:
            log_test(
                "Login with wrong password",
                False,
                f"Expected 401, got {response.status_code}: {response.text}"
            )
    except Exception as e:
        log_test("Login with wrong password", False, f"Exception: {e}")

def test_login_old_password():
    """Test 3: POST /api/auth/login with old password (should be rejected)"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": ADMIN_USERNAME, "password": OLD_PASSWORD},
            timeout=10
        )
        
        if response.status_code == 401:
            data = response.json()
            if "detail" in data and data["detail"] == "Username atau password salah":
                log_test(
                    "Login with old password (Elastech@2026) rejected",
                    True,
                    f"Old password correctly rejected with 401"
                )
            else:
                log_test(
                    "Login with old password (Elastech@2026) rejected",
                    False,
                    f"Got 401 but wrong message: {data}"
                )
        else:
            log_test(
                "Login with old password (Elastech@2026) rejected",
                False,
                f"Expected 401, got {response.status_code}: {response.text}"
            )
    except Exception as e:
        log_test("Login with old password (Elastech@2026) rejected", False, f"Exception: {e}")

def test_auth_me_with_token(token: str):
    """Test 4: GET /api/auth/me with valid token"""
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"X-Session-Token": token},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "username" in data and data["username"] == ADMIN_USERNAME:
                log_test(
                    "GET /api/auth/me with valid token",
                    True,
                    f"Got username={data['username']}, ttl_minutes={data.get('ttl_minutes')}"
                )
            else:
                log_test(
                    "GET /api/auth/me with valid token",
                    False,
                    f"Response structure incorrect: {data}"
                )
        else:
            log_test(
                "GET /api/auth/me with valid token",
                False,
                f"Expected 200, got {response.status_code}: {response.text}"
            )
    except Exception as e:
        log_test("GET /api/auth/me with valid token", False, f"Exception: {e}")

def test_auth_me_without_token():
    """Test 5: GET /api/auth/me without token"""
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            timeout=10
        )
        
        if response.status_code == 401:
            log_test(
                "GET /api/auth/me without token",
                True,
                f"Got expected 401"
            )
        else:
            log_test(
                "GET /api/auth/me without token",
                False,
                f"Expected 401, got {response.status_code}: {response.text}"
            )
    except Exception as e:
        log_test("GET /api/auth/me without token", False, f"Exception: {e}")

def test_protected_route_without_token():
    """Test 6: Access protected route without token"""
    try:
        response = requests.get(
            f"{BASE_URL}/copper/tests",
            timeout=10
        )
        
        if response.status_code == 401:
            data = response.json()
            if "detail" in data and data["detail"] == "Tidak terautentikasi. Silakan login.":
                log_test(
                    "Protected route (GET /api/copper/tests) without token",
                    True,
                    f"Got expected 401 with message: {data['detail']}"
                )
            else:
                log_test(
                    "Protected route (GET /api/copper/tests) without token",
                    False,
                    f"Got 401 but wrong message: {data}"
                )
        else:
            log_test(
                "Protected route (GET /api/copper/tests) without token",
                False,
                f"Expected 401, got {response.status_code}: {response.text}"
            )
    except Exception as e:
        log_test("Protected route (GET /api/copper/tests) without token", False, f"Exception: {e}")

def test_protected_route_with_token(token: str):
    """Test 7: Access protected route with valid token"""
    try:
        response = requests.get(
            f"{BASE_URL}/copper/tests",
            headers={"X-Session-Token": token},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                log_test(
                    "Protected route (GET /api/copper/tests) with valid token",
                    True,
                    f"Got 200 with {len(data)} records"
                )
            else:
                log_test(
                    "Protected route (GET /api/copper/tests) with valid token",
                    False,
                    f"Expected list, got: {type(data)}"
                )
        else:
            log_test(
                "Protected route (GET /api/copper/tests) with valid token",
                False,
                f"Expected 200, got {response.status_code}: {response.text}"
            )
    except Exception as e:
        log_test("Protected route (GET /api/copper/tests) with valid token", False, f"Exception: {e}")

def test_logout_and_token_invalidation(token: str):
    """Test 8: POST /api/auth/logout and verify token is invalidated"""
    try:
        # First, logout
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            headers={"X-Session-Token": token},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") == True:
                log_test(
                    "POST /api/auth/logout",
                    True,
                    f"Logout successful: {data}"
                )
                
                # Now try to use the same token on /api/auth/me
                response2 = requests.get(
                    f"{BASE_URL}/auth/me",
                    headers={"X-Session-Token": token},
                    timeout=10
                )
                
                if response2.status_code == 401:
                    log_test(
                        "Token invalidated after logout (GET /api/auth/me)",
                        True,
                        f"Token correctly rejected with 401"
                    )
                else:
                    log_test(
                        "Token invalidated after logout (GET /api/auth/me)",
                        False,
                        f"Expected 401, got {response2.status_code}: {response2.text}"
                    )
            else:
                log_test(
                    "POST /api/auth/logout",
                    False,
                    f"Logout response incorrect: {data}"
                )
        else:
            log_test(
                "POST /api/auth/logout",
                False,
                f"Expected 200, got {response.status_code}: {response.text}"
            )
    except Exception as e:
        log_test("POST /api/auth/logout and token invalidation", False, f"Exception: {e}")

def main():
    print("\n🧪 AUTHENTICATION FLOW TESTING")
    print("=" * 80)
    
    # Test 1: Login with correct credentials
    print("\n📝 Test 1: Login with correct credentials")
    token = test_login_correct_credentials()
    
    if not token:
        print("\n❌ CRITICAL: Cannot proceed without valid token from login")
        print_summary()
        sys.exit(1)
    
    # Test 2: Login with wrong password
    print("\n📝 Test 2: Login with wrong password")
    test_login_wrong_password()
    
    # Test 3: Login with old password
    print("\n📝 Test 3: Login with old password (should be rejected)")
    test_login_old_password()
    
    # Test 4: GET /api/auth/me with valid token
    print("\n📝 Test 4: GET /api/auth/me with valid token")
    test_auth_me_with_token(token)
    
    # Test 5: GET /api/auth/me without token
    print("\n📝 Test 5: GET /api/auth/me without token")
    test_auth_me_without_token()
    
    # Test 6: Protected route without token
    print("\n📝 Test 6: Access protected route without token")
    test_protected_route_without_token()
    
    # Test 7: Protected route with valid token
    print("\n📝 Test 7: Access protected route with valid token")
    test_protected_route_with_token(token)
    
    # Test 8: Logout and verify token invalidation
    print("\n📝 Test 8: Logout and verify token invalidation")
    test_logout_and_token_invalidation(token)
    
    print_summary()

def print_summary():
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {tests_passed + tests_failed}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print("=" * 80)
    
    if tests_failed > 0:
        print("\n❌ FAILED TESTS:")
        for result in test_results:
            if not result["passed"]:
                print(f"  - {result['name']}")
                if result["details"]:
                    print(f"    {result['details']}")
    else:
        print("\n✅ ALL TESTS PASSED!")
    
    print("\n")

if __name__ == "__main__":
    main()
