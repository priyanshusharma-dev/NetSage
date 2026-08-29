"""
Live Health Check & REST API Verification Suite
================================================

Validates live running FastAPI server on http://127.0.0.1:8000
and live running Next.js frontend on http://localhost:3000.
"""

import httpx
import time
import json

def check_live_system():
    print("=" * 75)
    print(" [Live Health Check] Testing Running Backend (8000) & Frontend (3000) ")
    print("=" * 75)

    client = httpx.Client(timeout=10.0)

    # 1. Check Backend Swagger Docs
    print("\n[1] Testing GET http://127.0.0.1:8000/docs ...")
    res = client.get("http://127.0.0.1:8000/docs")
    print(f"    Status: {res.status_code} OK")
    assert res.status_code == 200

    # 2. Check Topology Status Endpoint
    print("\n[2] Testing GET /api/v1/topology/status ...")
    res = client.get("http://127.0.0.1:8000/api/v1/topology/status")
    print(f"    Status: {res.status_code}")
    top_data = res.json()
    print(f"    - Nodes loaded: {len(top_data['nodes'])}")
    print(f"    - Links loaded: {len(top_data['links'])}")
    print(f"    - Mode: {top_data['mode']}")
    assert res.status_code == 200
    assert len(top_data['nodes']) == 8

    # 3. Test Fault Injection via REST API (Interface Down)
    print("\n[3] Testing POST /api/v1/fault/inject (interface_down) ...")
    res = client.post(
        "http://127.0.0.1:8000/api/v1/fault/inject",
        json={"fault_type": "interface_down", "params": {"target_node": "HQ-R1", "target_interface": "GigabitEthernet0/1"}}
    )
    print(f"    Status: {res.status_code}")
    fault_res = res.json()
    print(f"    - Injected: {fault_res['fault']['description']}")
    assert res.status_code == 200

    # 4. Test Live Autonomous Diagnosis via REST API
    print("\n[4] Testing POST /api/v1/diagnose ...")
    res = client.post("http://127.0.0.1:8000/api/v1/diagnose")
    print(f"    Status: {res.status_code}")
    diag_res = res.json()
    print(f"    - Diagnosis Status: {diag_res['status']}")
    print(f"    - Confidence: {diag_res['confidence_score']}%")
    print(f"    - Root Cause: {diag_res['final_root_cause']}")
    print(f"    - Recommended CLI Fix:\n      {diag_res['recommended_fix'].replace(chr(10), ' | ')}")
    print(f"    - Evidence Chunks: {len(diag_res.get('retrieved_evidence', []))}")
    assert res.status_code == 200
    assert diag_res['fallback_triggered'] is False

    # 5. Test History & Stats via REST API
    print("\n[5] Testing GET /api/v1/history and GET /api/v1/stats ...")
    res_hist = client.get("http://127.0.0.1:8000/api/v1/history?limit=5")
    res_stats = client.get("http://127.0.0.1:8000/api/v1/stats")
    print(f"    - History Status: {res_hist.status_code} (Items: {len(res_hist.json())})")
    print(f"    - Stats: {res_stats.json()}")
    assert res_hist.status_code == 200
    assert res_stats.status_code == 200

    # 6. Test Reset via REST API
    print("\n[6] Testing POST /api/v1/fault/reset ...")
    res = client.post("http://127.0.0.1:8000/api/v1/fault/reset")
    print(f"    Status: {res.status_code}")
    assert res.status_code == 200

    # 7. Check Frontend Next.js Server
    print("\n[7] Testing GET http://localhost:3000/ (Next.js Dashboard) ...")
    res_front = client.get("http://localhost:3000/")
    print(f"    Status: {res_front.status_code}")
    assert res_front.status_code == 200
    print("    - Next.js HTML response received successfully!")

    print("\n" + "=" * 75)
    print(" [ALL CHECKS PASSED] Backend API & Frontend Dashboard Running Live! ")
    print("=" * 75)

if __name__ == "__main__":
    check_live_system()
