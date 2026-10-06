# Blueprint: Containerized AI Email Subject Line Generator

This blueprint sets up a full-stack AI application using FastAPI, Google Gemini API, and Docker. 
FastAPI acts as the single web server that hosts both the API endpoints and the frontend static files.

---

## 1. Project Directory Structure
Ensure your files are placed in this exact hierarchy:
```text
ai-subject-generator/
│
├── static/
│   └── index.html       # Frontend User Interface
├── main.py              # FastAPI Backend Script
├── requirements.txt     # Python System Dependencies
└── Dockerfile           # Deployment Container Configuration
```

---

## 2. System Configurations & Codebase

### File: `requirements.txt`
```text
fastapi
uvicorn
google-genai
pydantic
```

### File: `main.py`
```python
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai

app = FastAPI(title="AI Subject Line Generator")

# 1. Serve frontend index.html at root path (/)
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# 2. Mount static folder for frontend asset management
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. Global client setup to preserve cloud connection pool
try:
    ai_client = genai.Client()
except Exception as e:
    print(f"Connection Initialization Error: {e}")

class GenerationRequest(BaseModel):
    topic: str
    tone: str

# 4. Asynchronous performance-maximized AI core endpoint
@app.post("/generate-subjects")
async def generate_subject_lines(request: GenerationRequest):
    if not request.topic or not request.tone:
        raise HTTPException(status_code=400, detail="Missing required payload parameters.")
    
    prompt = f"Generate 5 high-converting email subject lines. Topic: {request.topic}. Tone: {request.tone}. Output a numbered list 1-5 only."
    
    try:
        # Utilize native async client mapping (aio) to eliminate server freezing
        response = await ai_client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"subject_lines": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloud AI Inference Failed: {str(e)}")
```

### File: `static/index.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Subject Line Generator</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; color: #333; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #ccc; box-sizing: border-box; }
        button { background-color: #007bff; color: white; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 6px; border: 1px solid #e9ecef; white-space: pre-wrap; font-size: 14px; }
    </style>
</head>
<body>
    <h2>🚀 AI Email Subject Line Generator</h2>
    <label for="topic">What is your email campaign about?</label>
    <input type="text" id="topic" placeholder="e.g., Year-End 50% discount sale on sports shoes">
    
    <label for="tone">Choose Marketing Tone:</label>
    <select id="tone">
        <option value="Professional">💼 Professional</option>
        <option value="Urgent">⏰ Urgent / FOMO</option>
        <option value="Funny">🎉 Funny & Engaging</option>
    </select>
    
    <button onclick="generateSubjects()">Generate High-Converting Subjects</button>
    
    <h3>Generated Options:</h3>
    <pre id="output">Your AI variations will display here...</pre>

    <script>
        async function generateSubjects() {
            const topic = document.getElementById('topic').value;
            const tone = document.getElementById('tone').value;
            const output = document.getElementById('output');
            
            if (!topic) {
                alert("Please type a topic first!");
                return;
            }
            
            output.innerText = "Analyzing variables and generating copywriting options...";
            
            try {
                // Relies on unified routing since frontend/backend share the same Docker domain
                const response = await fetch('/generate-subjects', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic, tone })
                });
                const data = await response.json();
                output.innerText = data.subject_lines || data.detail;
            } catch (err) {
                output.innerText = "Network Error: Could not bind session to backend API.";
            }
        }
    </script>
</body>
</html>
```

### File: `Dockerfile`
```dockerfile
# Optimized Python footprint for high performance Cloud instances
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Run Uvicorn via multi-threaded production worker configuration
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## 3. GitHub Copilot Execution Prompts

Copy and paste these direct instruction sets into your **GitHub Copilot Chat (`@workspace`)** inside VS Code to let it implement changes for you:

* **To add text logs:** 
  > `"@workspace update main.py to append every generated subject line outcome into a local text log file named generation_history.txt every time the endpoint is executed."`
* **To add premium frontend styling:** 
  > `"@workspace add a modern dark-mode toggler switch inside static/index.html using clean CSS transitions."`
* **To write tests:**
  > `"@workspace write a complete backend automation test script using pytest and TestClient to validate the /generate-subjects route input schemas."`
