import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing Backend API...")
    
    # 1. Health/Root Check
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"Root: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Failed to connect to root: {e}")
        return

    # 2. Create Session
    print("\nCreating Session...")
    r = requests.post(f"{BASE_URL}/api/sessions", json={"title": "Test Chat"})
    print(f"Create Session: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
        return
    session = r.json()
    session_id = session['id']
    print(f"Session ID: {session_id}")

    # 3. Chat (Streaming)
    print("\nSending Message 'Hello'...")
    r = requests.post(f"{BASE_URL}/api/chat", json={"session_id": session_id, "message": "Hello, simply say 'Hi there'"}, stream=True)
    
    print("Streaming Response:")
    for chunk in r.iter_content(chunk_size=None):
        if chunk:
            print(chunk.decode('utf-8'), end="", flush=True)
    print("\n\nStream Finished.")

    # 4. Verify History
    print("\nVerifying History...")
    r = requests.get(f"{BASE_URL}/api/sessions/{session_id}")
    print(f"Get History: {r.status_code}")
    history = r.json()
    print(f"Messages count: {len(history.get('messages', []))}")

if __name__ == "__main__":
    time.sleep(2) # Give server time to start
    test_api()
