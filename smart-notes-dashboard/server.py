import os
import json
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 3000
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(CURRENT_DIR, 'public')

# Helper to read .env file manually (zero-dependency approach)
def load_env():
    env_vars = {}
    env_path = os.path.join(CURRENT_DIR, '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, val = line.split('=', 1)
                        env_vars[key.strip()] = val.strip().strip('"').strip("'")
        except Exception as e:
            print(f"Warning: Failed to read .env file: {e}")
    return env_vars

ENV = load_env()

class DashboardHandler(SimpleHTTPRequestHandler):
    # Support CORS preflight options request
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/analyze':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                notes_text = data.get('notes', '')
                
                # Fetch config from env
                api_key = ENV.get('API_KEY', os.environ.get('API_KEY', ''))
                base_url = ENV.get('BASE_URL', os.environ.get('BASE_URL', 'https://api.groq.com/openai/v1'))
                model = ENV.get('MODEL', os.environ.get('MODEL', 'llama-3.3-70b-specdec'))
                
                if not api_key:
                    # Simulated output fallback
                    response_data = self.generate_simulated_response(notes_text)
                    self.send_json_response(response_data)
                    return
                
                # Real API call
                response_data = self.call_llm_api(api_key, base_url, model, notes_text)
                self.send_json_response(response_data)
                
            except Exception as e:
                print(f"Error handling request: {e}")
                self.send_error_response(500, str(e))
        else:
            self.send_error_response(404, "Endpoint not found")

    def do_GET(self):
        # Serve static files from the public folder
        if self.path == '/api/prompt-config':
            self.serve_prompt_config()
            return
            
        # Standard static file serving
        super().do_GET()

    def translate_path(self, path):
        # By default, SimpleHTTPRequestHandler looks in the current working directory.
        # We redirect it to look into the 'public' subfolder instead.
        if path == '/' or path == '':
            return os.path.join(PUBLIC_DIR, 'index.html')
            
        # Parse query params or hash if any (clean paths)
        clean_path = path.split('?')[0].split('#')[0]
        relative_path = clean_path.lstrip('/')
        full_path = os.path.join(PUBLIC_DIR, relative_path)
        
        # If folder requested, serve index.html inside it
        if os.path.isdir(full_path):
            return os.path.join(full_path, 'index.html')
            
        return full_path

    def serve_prompt_config(self):
        config_path = os.path.join(CURRENT_DIR, 'prompt-config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self.send_json_response(config_data)
            except Exception as e:
                self.send_error_response(500, f"Failed to read prompt-config: {e}")
        else:
            self.send_error_response(404, "prompt-config.json not found")

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    def generate_simulated_response(self, text):
        text_lower = text.lower()
        if "quantum" in text_lower:
            summary = [
                "Quantum superposition allows particles to exist in multiple states simultaneously (e.g. 0 and 1) until measured.",
                "Quantum entanglement creates a link where the state of one particle instantly dictates the state of another, regardless of physical separation.",
                "Qubits utilize superposition, entanglement, and interference to execute complex computational tasks exponentially faster than classical bits.",
                "Coherence is highly delicate; environmental disturbances cause decoherence, resulting in calculation errors."
            ]
            action_items = [
                "Define the physical differences between a classical bit and a quantum qubit.",
                "Sketch a diagram representing quantum entanglement between two particles.",
                "Watch the conceptual animation on decoherence and quantum error correction.",
                "Solve practice exercises 1-4 on quantum gate operations and circuit paths."
            ]
        elif "cell" in text_lower or "biology" in text_lower or "mitosis" in text_lower:
            summary = [
                "Mitosis is the process of cell division that results in two daughter cells containing identical genomic blueprints.",
                "Mitosis proceeds in four main sequential stages: Prophase, Metaphase, Anaphase, and Telophase (PMAT).",
                "Spindle fibers attach to sister chromatids at their kinetochores to accurately pull them to opposite poles.",
                "Cytokinesis completes the process by physically dividing the cytoplasm and enclosing the two new cells."
            ]
            action_items = [
                "Label the cellular diagrams representing each stage of mitosis.",
                "Create a comparison table showing the key differences between mitosis and meiosis.",
                "Summarize the functional role of microtubule spindle fibers during Metaphase.",
                "Take the mitosis cell-cycle self-assessment quiz on EduFlick AI."
            ]
        else:
            # Default response based on generic notes or active learning
            summary = [
                "Active recall and spaced repetition represent the most evidence-based cognitive strategies for long-term study retention.",
                "Structuring messy notes into modular, visual takeaways dramatically reduces mental fatigue and cognitive overload.",
                "Action items bridge the gap between passive reading and active comprehension by creating measurable, structured tasks.",
                "Continuous self-testing and summarizing in one's own words builds strong synaptic pathways for recall."
            ]
            action_items = [
                "Convert these takeaways into 5 high-yield flashcards for self-testing.",
                "Set a calendar reminder to review these action items in exactly 48 hours.",
                "Teach the core concept of this transcript to a study group member without looking at the notes.",
                "Solve the practical assignment checklist to test your conceptual understanding."
            ]
        return {
            "summary": summary,
            "actionItems": action_items,
            "mode": "simulated"
        }

    def call_llm_api(self, api_key, base_url, model, notes_text):
        system_prompt = (
            "You are an expert educational AI assistant. Your task is to analyze disorganized, messy study notes "
            "or lecture transcripts and convert them into clean, structured takeaways and study action items.\n"
            "You MUST respond ONLY with a valid JSON object matching the following structure:\n"
            "{\n"
            "  \"summary\": [\"Short takeaway 1\", \"Short takeaway 2\", ...],\n"
            "  \"actionItems\": [\"Actionable task 1\", \"Actionable task 2\", ...]\n"
            "}\n"
            "Constraints:\n"
            "- Keep summary points short, clear, and educational.\n"
            "- Keep action items concrete, practical, and starting with an action verb.\n"
            "- Do not include markdown code block syntax (like ```json) or conversational chatter.\n"
            "- Output valid, parseable JSON."
        )
        
        url = base_url.rstrip('/') + '/chat/completions'
        payload = {
            "model": model,
            "messages": [
                {"role": "system", content: system_prompt},
                {"role": "user", content: f"Here are the notes to analyze:\n\n{notes_text}"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as res:
                response_body = res.read().decode('utf-8')
                result_json = json.loads(response_body)
                content = result_json['choices'][0]['message']['content']
                # Parse the content to make sure it is valid JSON
                parsed_content = json.loads(content)
                return {
                    "summary": parsed_content.get("summary", []),
                    "actionItems": parsed_content.get("actionItems", []),
                    "mode": "api"
                }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"API Error {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Failed to process API call: {str(e)}")

if __name__ == '__main__':
    # Make sure public dir exists
    if not os.path.exists(PUBLIC_DIR):
        os.makedirs(PUBLIC_DIR)
        
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"Server running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()
