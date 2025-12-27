import sys
import time
import requests

def check_server_health():
    url = "http://127.0.0.1:8001/health"
    print(f"Checking {url}...")
    
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Server is running.")
            print(f"   Project: {data.get('project')}")
            print(f"   LLM URL: {data.get('config_check', {}).get('llm_base_url')}")
        else:
            print(f"❌ Failed: Status Code {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is uvicorn running?")
        print("Run: cd backend && uvicorn app.main:app --reload")
        sys.exit(1)

if __name__ == "__main__":
    # Give uvicorn a moment to start if running via script runner (optional)
    time.sleep(1)
    check_server_health()