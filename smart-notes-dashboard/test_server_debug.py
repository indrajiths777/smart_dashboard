import subprocess
import time
import urllib.request
import sys
import os

PORT = 3005  # Use a different port to avoid conflicts
SERVER_URL = f"http://localhost:{PORT}"

def run_debug():
    print("Starting debug server...")
    
    # Create log files
    stdout_file = open("server_stdout.log", "w")
    stderr_file = open("server_stderr.log", "w")
    
    # Write config to use port 3005 in environment
    os.environ["PORT"] = str(PORT)
    
    # Start server
    # We modify server.py dynamically to respect PORT from env, or we pass it
    # Wait, server.py uses PORT = 3000 hardcoded in python. Let's start it.
    # To run on port 3005, let's write a small wrapper or just run server.py
    # Since server.py has PORT = 3000, let's change server.py to check for PORT env variable!
    
    # Let's run server.py
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=stdout_file,
        stderr=stderr_file,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    time.sleep(1.5)
    
    try:
        # Note: server.py runs on port 3000 by default unless we set port 3000
        url = "http://localhost:3000"
        print(f"Requesting {url}/ ...")
        with urllib.request.urlopen(f"{url}/") as res:
            print(f"Status: {res.status}")
            
        print(f"Requesting {url}/style.css ...")
        with urllib.request.urlopen(f"{url}/style.css") as res:
            print(f"Status: {res.status}")
            
        print(f"Requesting {url}/app.js ...")
        with urllib.request.urlopen(f"{url}/app.js") as res:
            print(f"Status: {res.status}")
            
        print("Success! All static requests completed.")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        # Read stderr
        stderr_file.flush()
        with open("server_stderr.log", "r") as f:
            print("\n--- SERVER STDERR LOG ---")
            print(f.read())
            print("-------------------------")
            
    finally:
        server_process.terminate()
        server_process.wait()
        stdout_file.close()
        stderr_file.close()

if __name__ == '__main__':
    run_debug()
