from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
import os

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            notes_text = data.get('notes', '')
            
            # Fetch config directly from Vercel injected environment variables
            api_key = os.environ.get('API_KEY', '')
            base_url = os.environ.get('BASE_URL', 'https://api.groq.com/openai/v1')
            model = os.environ.get('MODEL', 'llama-3.3-70b-specdec')
            
            if not api_key:
                # Simulated output fallback
                response_data = self.generate_simulated_response(notes_text)
                self.send_json_response(response_data)
                return
            
            # Real API call
            response_data = self.call_llm_api(api_key, base_url, model, notes_text)
            self.send_json_response(response_data)
            
        except Exception as e:
            self.send_error_response(500, str(e))

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
