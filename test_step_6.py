import sys
import os
import json
import logging
from fastapi.testclient import TestClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestStep6")

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from app.main import app
    from app.core.config import settings
except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)


def test_api_integration():
    print("\n--- Testing API Layer Integration ---\n")

    # 1. Initialize TestClient
    client = TestClient(app)

    # 2. Test Health Check
    print("1. Testing /health...")
    response = client.get("/health")
    if response.status_code == 200:
        print(f"✅ Health Check Passed: {response.json()}")
    else:
        print(f"❌ Health Check Failed: {response.status_code}")
        sys.exit(1)

    # 3. Test POST /api/v1/game/turn
    print("\n2. Testing POST /api/v1/game/turn...")

    # Ensure state.json exists
    if not os.path.exists("state.json"):
        print("❌ 'state.json' not found. Please verify the file exists in the root.")
        sys.exit(1)

    # Prepare payload
    payload = {"user_character_name": "Sveta", "user_input": "I look around the room."}

    print(f"   Sending payload: {json.dumps(payload)}")
    print("   ...Processing (Waiting for Local LLM)...")

    try:
        # Note: This might take time depending on local LLM speed
        url = f"{settings.API_V1_STR}/game/turn"
        response = client.post(url, json=payload, timeout=60.0)

        if response.status_code == 200:
            data = response.json()
            print("✅ Turn Processed Successfully via API!")
            print(f"   - AI Character: {data.get('ai_character_name')}")
            print(f"   - Story Segment: {data.get('story_part')[:100]}...")
            print(f"   - Completed Actions: {data.get('completed_actions')}")
        else:
            print(f"❌ API Request Failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Exception during API call: {e}")


if __name__ == "__main__":
    test_api_integration()
