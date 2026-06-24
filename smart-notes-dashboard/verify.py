import subprocess
import time
import urllib.request
import urllib.error
import json
import sys
import os

PORT = 3000
SERVER_URL = f"http://localhost:{PORT}"

def run_tests():
    print("==================================================")
    print("Starting Automated Server & API Verification Tests")
    print("==================================================")
    
    # 1. Start Python Server in background
    print("\n[1/5] Starting server.py in background...")
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    # Wait for server to boot
    time.sleep(1.5)
    
    # Check if process is still running
    if server_process.poll() is not None:
        print("[FAIL] Error: Server failed to start immediately.")
        sys.exit(1)
        
    print("[SUCCESS] Server successfully started.")
    
    try:
        # 2. Test Static File Server
        print("\n[2/5] Testing index.html file delivery...")
        try:
            with urllib.request.urlopen(f"{SERVER_URL}/") as res:
                status = res.status
                html = res.read().decode('utf-8')
                if status == 200 and "<html" in html:
                    print("[SUCCESS] HTML delivery verified (200 OK).")
                else:
                    raise Exception(f"Invalid status {status} or missing HTML tag.")
        except Exception as e:
            print(f"[FAIL] Failed: Could not get index.html: {e}")
            raise e
            
        # 3. Test Static Assets Routing
        print("\n[3/5] Testing CSS and JS routing...")
        try:
            with urllib.request.urlopen(f"{SERVER_URL}/style.css") as res:
                if res.status == 200:
                    print("[SUCCESS] CSS stylesheet routing verified.")
            with urllib.request.urlopen(f"{SERVER_URL}/app.js") as res:
                if res.status == 200:
                    print("[SUCCESS] Client JS script routing verified.")
        except Exception as e:
            print(f"[FAIL] Failed: Asset routing failed: {e}")
            raise e

        # 4. Test Prompt Config Endpoint
        print("\n[4/5] Testing GET /api/prompt_config API endpoint...")
        try:
            with urllib.request.urlopen(f"{SERVER_URL}/api/prompt_config") as res:
                status = res.status
                body = json.loads(res.read().decode('utf-8'))
                if status == 200 and "systemInstructions" in body and "jsonSchema" in body:
                    print("[SUCCESS] Prompt Config API endpoint verified (200 OK).")
                else:
                    raise Exception("Missing required schema fields in response.")
        except Exception as e:
            print(f"[FAIL] Failed: /api/prompt-config failed: {e}")
            raise e

        # 5. Test Note Analysis Endpoint (Simulated Mode)
        print("\n[5/5] Testing POST /api/analyze API endpoint (Simulated Mode)...")
        payload = json.dumps({"notes": "Tell me about mitosis and cell biology."}).encode('utf-8')
        req = urllib.request.Request(
            f"{SERVER_URL}/api/analyze",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as res:
                status = res.status
                body = json.loads(res.read().decode('utf-8'))
                if status == 200:
                    print("[SUCCESS] Analysis endpoint returned 200 OK.")
                    # Check JSON schema format
                    if "summary" in body and "actionItems" in body and "mode" in body:
                        print("[SUCCESS] JSON schema matches specifications.")
                        print(f"   Mode: {body['mode']}")
                        print(f"   Summary items: {len(body['summary'])}")
                        print(f"   Checklist items: {len(body['actionItems'])}")
                    else:
                        raise Exception("Analysis response is missing required properties.")
                else:
                    raise Exception(f"Returned status {status}")
        except Exception as e:
            print(f"[FAIL] Failed: POST /api/analyze failed: {e}")
            raise e
            
        print("\n==================================================")
        print("SUCCESS: All Automated Tests Passed Successfully!")
        print("==================================================")
        
    finally:
        # Shut down background server
        print("\nStopping background server process...")
        server_process.terminate()
        server_process.wait()
        print("Server process shut down.")

if __name__ == '__main__':
    run_tests()
