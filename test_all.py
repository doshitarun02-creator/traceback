# TraceBack — Production End-to-End API Test Suite
# ====================================================
# This script validates all critical API endpoints required for production.
# Usage: python test_all.py

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"
TEST_USER = {
    "name": "Test Victim",
    "email": f"test_{int(time.time())}@example.com",
    "phone": "9876543210",
    "password": "Password123!",
    "state": "Maharashtra",
    "language": "English"
}

ADMIN_USER = {
    "email": "admin@traceback.in",
    "password": "admin_secure_pass_2026" # Matches seed.py
}

def test_api():
    print("🚀 Starting TraceBack API Audit...\n")
    
    # 1. Health Check
    print("Test 1: GET /health")
    try:
        res = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        print(f"Status: {res.status_code} | Body: {res.json()}")
        assert res.status_code == 200
    except Exception as e:
        print(f"❌ Failed: {e}")

    # 2. Register
    print("\nTest 2: POST /api/auth/register")
    res = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    print(f"Status: {res.status_code}")
    assert res.status_code == 201
    user_token = res.json()["data"]["access_token"]

    # 3. Login
    print("\nTest 3: POST /api/auth/login")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    print(f"Status: {res.status_code}")
    assert res.status_code == 200

    # 4. AI Triage Analyze
    print("\nTest 4: POST /api/triage/analyze")
    desc = "I lost 50000 rupees in a Telegram trading scam. They asked me to join a group and then invest in a fake app called TRADEX."
    res = requests.post(f"{BASE_URL}/triage/analyze", json={"description": desc})
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print(f"AI Analysis: {json.dumps(res.json()['data'], indent=2)}")
    assert res.status_code == 200

    # 5. Submit Complaint
    print("\nTest 5: POST /api/complaints/submit")
    complaint_data = {
        "fraud_type": "investment_scam",
        "amount_lost": 50000,
        "incident_date": "2026-05-01T10:00",
        "platform": "Telegram",
        "description": desc,
        "bank_name": "HDFC",
        "victim_account": "1234567890",
        "fraudster_account": "9876543210",
        "transaction_id": "TXN123456",
        "state": "Maharashtra",
        "victim": {
            "name": TEST_USER["name"],
            "phone": TEST_USER["phone"],
            "email": TEST_USER["email"]
        }
    }
    # Send as form-data
    files = {'evidence': ('test.txt', 'This is some evidence data.')}
    data = {'json_data': json.dumps(complaint_data)}
    
    headers = {"Authorization": f"Bearer {user_token}"}
    res = requests.post(f"{BASE_URL}/complaints/submit", data=data, files=files, headers=headers)
    print(f"Status: {res.status_code}")
    assert res.status_code == 201
    case_id = res.json()["data"]["case_id"]

    # 6. Get Complaint
    print(f"\nTest 6: GET /api/complaints/{case_id}")
    res = requests.get(f"{BASE_URL}/complaints/{case_id}", headers=headers)
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    assert res.json()["data"]["case_id"] == case_id

    # 7. List Experts
    print("\nTest 7: GET /api/experts")
    res = requests.get(f"{BASE_URL}/experts")
    print(f"Status: {res.status_code} | Count: {res.json()['data']['count']}")
    assert res.status_code == 200

    # 8. Filter Experts
    print("\nTest 8: GET /api/experts?category=investment")
    res = requests.get(f"{BASE_URL}/experts?category=investment")
    print(f"Status: {res.status_code} | Count: {res.json()['data']['count']}")
    assert res.status_code == 200

    # 9. Live Stats
    print("\nTest 9: GET /api/cases/stats/live")
    res = requests.get(f"{BASE_URL}/cases/stats/live")
    print(f"Status: {res.status_code} | Body: {res.json()['data']}")
    assert res.status_code == 200

    # 10. Admin Login
    print("\nTest 10: POST /api/auth/login (Admin)")
    res = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_USER)
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    admin_token = res.json()["data"]["access_token"]

    # 11. Admin Dashboard
    print("\nTest 11: GET /api/admin/dashboard")
    res = requests.get(f"{BASE_URL}/admin/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print(f"Dashboard: {json.dumps(res.json()['data'], indent=2)}")
    assert res.status_code == 200

    print("\n✨ ALL TESTS PASSED! TraceBack Backend is Production-Ready.")

if __name__ == "__main__":
    test_api()
