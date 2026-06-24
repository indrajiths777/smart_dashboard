# AI-Powered Smart Notes & Action Item Dashboard

This is a premium, single-page web dashboard (Tomatrix Task 14) that takes a block of raw, disorganized study notes or transcripts, structures them into a list of key summaries, and creates an interactive study action-items checklist.

## Features

- **Ingestion Panel**: Paste messy, unstructured notes or video transcripts.
- **Quick Sample Buttons**: Load pre-packaged Cell Biology (mitosis) or Quantum Physics transcripts with a single click.
- **Key Takeaways Dashboard**: A beautiful, animated card listing the extracted educational concepts.
- **Interactive Checklist**: A study checklist where checking items strikes them out and dims them to 50% opacity.
- **Visual Progress Bar**: Track study completion percentage in real-time.
- **Confetti Celebration**: Canvas-rendered confetti explosion when you complete 100% of your checklist.
- **Interactive JSON Prompt Configuration**: Toggle and view the exact system instructions and JSON schema used to query the LLM.
- **Flexible Backend**: Runs on Python 3 using only built-in libraries (zero external package dependencies). Supports Groq, Grok, or offline Simulated Mode out-of-the-box.

---

## Getting Started

### 1. Start the Server
Open a terminal in the project directory (`D:\smart-notes-dashboard`) and run:
```bash
python server.py
```
You should see:
```text
Server running at http://localhost:3000
```

### 2. Open the Dashboard
Open your browser and navigate to:
[http://localhost:3000](http://localhost:3000)

---

## Configuring Live AI (Optional)

By default, the server runs in **Simulated Mode** (so you can test it immediately without configuration). To connect to a live LLM:

1. Open the `.env` file in the project folder.
2. Configure your API key and base URL:

**For Groq (Recommended for ultra-fast processing):**
```env
API_KEY=gsk_your_groq_api_key_here
BASE_URL=https://api.groq.com/openai/v1
MODEL=llama-3.3-70b-specdec
```

**For Grok (xAI):**
```env
API_KEY=xai_your_grok_api_key_here
BASE_URL=https://api.x.ai/v1
MODEL=grok-2
```
3. Restart the server. The connection badge in the top-right header will turn green and read **Live API Mode**.

---

## How to Record the Demo Video (1–2 Minutes)

A 1-2 minute demo video is a required deliverable. Here is a recommended recording walkthrough script:

1. **Introduction (10 seconds)**:
   - Start recording at `http://localhost:3000`.
   - Show the header, the dark glassmorphic design, and the connection badge.
2. **Show Prompt Configuration (15 seconds)**:
   - Click the **JSON Prompt Schema** accordion under the input panel to expand it.
   - Briefly show the system instructions and JSON Schema that enforce structured outputs. Click it again to collapse it.
3. **Ingestion & Generation (35 seconds)**:
   - Click the **🧬 Cell Biology** sample button. Show that the textarea fills with disorganized mitosis notes.
   - Click the **Analyze Notes** button. Note the loading spinner and the disable state.
   - Once generated, point out the animated entrance of the **Key Summaries** and the **Action Items Checklist**.
4. **Interaction & Completion (30 seconds)**:
   - Begin checking off items in the **Action Items Checklist**.
   - Point out that checked items are struck through and dimmed in opacity, and the progress bar increases.
   - Check the final item and show the **Confetti Celebration** filling the screen!
