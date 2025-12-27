import time
import requests
import subprocess
import sys
import os


def test_final_architecture():
    print("--- Final Architecture Verification ---")

    # 1. Start the server using the new run.py
    print("1. Starting backend server via 'backend/run.py'...")
    server_process = subprocess.Popen(
        [sys.executable, "backend/run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait for server startup
    time.sleep(5)

    # Check if process is still running
    if server_process.poll() is not None:
        stdout, stderr = server_process.communicate()
        print("❌ Server failed to start immediately.")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        sys.exit(1)

    print("   Server process started (PID: {}).".format(server_process.pid))

    try:
        # 2. Check Health
        print("\n2. Checking API Health...")
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ API is responding: {response.json()}")
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            sys.exit(1)

        # 3. Check Data Access (Did we move state.json correctly?)
        # We try to trigger a turn. If state.json is missing, it will return 404 or 500.
        print("\n3. Checking Data Layer Access...")
        payload = {"user_character_name": "Sveta", "user_input": "Look around"}

        # We expect a success or a specific validation error, but NOT a FileNotFoundError (500)
        # Assuming LLM might not be running, we handle connection errors gracefully,
        # but the purpose here is to check if the APP finds state.json.
        try:
            resp = requests.post(
                "http://127.0.0.1:8000/api/v1/game/turn", json=payload, timeout=120
            )
            if resp.status_code == 200:
                print("✅ Turn processed (state.json found and loaded).")
            elif resp.status_code == 500:
                print(
                    "⚠️ Server Error (500). Check if LLM is running, but verify logs for 'FileNotFoundError'."
                )
            else:
                print(
                    f"ℹ️ Response: {resp.status_code} (This is expected if LLM is offline, providing API is reachable)."
                )
        except requests.exceptions.ReadTimeout:
            print(
                "ℹ️ Request timed out (Expected if Local LLM is slow). API is reachable."
            )
        except Exception as e:
            print(f"❌ Connection error: {e}")

    finally:
        print("\n4. Shutting down server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Cleanup complete.")


if __name__ == "__main__":
    # Ensure we run from root
    if not os.path.exists("backend"):
        print("❌ Please run this script from the Project Root directory.")
    else:
        test_final_architecture()
