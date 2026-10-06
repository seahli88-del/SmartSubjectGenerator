# AI Email Subject Line Generator

A small web application that generates five email subject line ideas with Google Gemini. FastAPI serves both the API and the static HTML interface.

## Project Layout

```text
.
├── ai-subject-generator/
│   ├── static/index.html
│   ├── main.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── tests/test_main.py
│   └── Dockerfile
├── copilot-blueprint.md
└── README.md
```

## Run Locally on Windows

From the repository root, create and activate a virtual environment, then install the dependencies:

```powershell
cd ai-subject-generator
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set your Gemini API key in the same PowerShell session and start the server:

```powershell
$env:GEMINI_API_KEY = "your-api-key"
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000>. FastAPI's interactive API documentation is at <http://127.0.0.1:8000/docs>.

## Tests

From the `ai-subject-generator` directory, install the development dependencies and run the API tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

## API

`POST /generate-subjects` accepts a topic and marketing tone:

```json
{
  "topic": "A 20% spring sale on running shoes",
  "tone": "Professional"
}
```

A successful response contains a `subject_lines` string. The endpoint allows five generation requests per client IP per minute. The `topic` and `tone` fields must not be blank.

## Deploy to Render

1. Push this repository to GitHub.
2. In Render, create a **Web Service** and connect the repository.
3. Set **Root Directory** to `ai-subject-generator` and use Docker deployment.
4. Add `GEMINI_API_KEY` in the service's **Environment** settings.
5. Deploy. The container listens on Render's `PORT` environment variable.

Rate limits use in-memory storage, so they apply per running app process and reset when it restarts. If you scale to multiple instances, configure shared Redis-backed rate-limit storage to enforce a single limit across them.

## Security

Do not commit API keys or `.env` files. Configure `GEMINI_API_KEY` in your local terminal or Render's environment settings instead.
