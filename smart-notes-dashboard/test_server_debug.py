import subprocess
import time
import urllib.request
import json
import sys
import os

PORT = 3010
SERVER_URL = f"http://localhost:{PORT}"

def run_debug():
    print("Starting debug server...")
    
    # Modify server.py dynamically to run on port 3010 in this script
    with open("server.py", "r", encoding="utf-8") as f:
        code = f.read()
    
    temp_code = code.replace("PORT = 3000", f"PORT = {PORT}")
    with open("server_temp.py", "w", encoding="utf-8") as f:
        f.write(temp_code)
        
    test_env = os.environ.copy()
    if "API_KEY" in test_env:
        del test_env["API_KEY"]
        
    server_process = subprocess.Popen(
        [sys.executable, "server_temp.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env=test_env
    )
    
    time.sleep(1.5)
    
    try:
        # Test POST /api/analyze
        print(f"Requesting POST {SERVER_URL}/api/analyze ...")
        payload = json.dumps({"notes": "mitosis biology"}).encode('utf-8')
        req = urllib.request.Request(
            f"{SERVER_URL}/api/analyze",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            print(f"Status: {res.status}")
            print(f"Response: {res.read().decode()}")
            
    except urllib.error.HTTPError as e:
        print(f"HTTPError occurred: {e.code} {e.reason}")
        try:
            print(f"Response body: {e.read().decode('utf-8')}")
        except Exception as read_err:
            print(f"Could not read response body: {read_err}")
    except Exception as e:
        print(f"Generic error occurred: {e}")
            
    finally:
        server_process.terminate()
        server_process.wait()
        # Clean up temp file
        if os.path.exists("server_temp.py"):
            os.remove("server_temp.py")

if __name__ == '__main__':
    run_debug()
