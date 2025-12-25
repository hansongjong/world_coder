import requests
import sys

def test_endpoint(name, url):
    print(f"[*] Testing {name} ({url})...", end=" ")
    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            print(f"✅ OK (Payload: {resp.json()})")
            return True
        else:
            print(f"❌ FAIL (Status: {resp.status_code})")
            return False
    except Exception as e:
        print(f"❌ FAIL (Error: {e})")
        return False

if __name__ == "__main__":
    print("=== SYSTEM INTEGRITY CHECK ===\n")
    
    # 1. Core Kernel Root Check
    core_ok = test_endpoint("Core Root", "http://127.0.0.1:8000/")
    
    # 2. Commerce Engine Root Check
    comm_ok = test_endpoint("Commerce Root", "http://127.0.0.1:8001/")
    
    # 3. Dashboard Check
    dash_ok = test_endpoint("Dashboard API", "http://127.0.0.1:8000/ops/status")

    print("\n=== SUMMARY ===")
    if core_ok and comm_ok and dash_ok:
        print("🎉 ALL SYSTEMS GO! The 404 logs are just browser noise.")
    else:
        print("⚠️  Some services are down. Please check the console logs.")