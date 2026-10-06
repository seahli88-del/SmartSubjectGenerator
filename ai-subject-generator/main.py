import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from pydantic import BaseModel

app = FastAPI(title="AI Subject Line Generator")


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")

try:
    ai_client = genai.Client()
except Exception as exc:
    ai_client = None
    print(f"Connection Initialization Error: {exc}")


class GenerationRequest(BaseModel):
    topic: str
    tone: str


@app.post("/generate-subjects")
async def generate_subject_lines(request: GenerationRequest):
    if not request.topic.strip() or not request.tone.strip():
        raise HTTPException(
            status_code=400,
            detail="Missing required payload parameters.",
        )
    if ai_client is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini is unavailable. Configure GEMINI_API_KEY and restart the server.",
        )

    prompt = (
        "Generate 5 high-converting email subject lines. "
        f"Topic: {request.topic}. Tone: {request.tone}. "
        "Output a numbered list 1-5 only."
    )

    try:
        response = await ai_client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return {"subject_lines": (response.text or "").strip()}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Cloud AI Inference Failed: {exc}",
        ) from exc
