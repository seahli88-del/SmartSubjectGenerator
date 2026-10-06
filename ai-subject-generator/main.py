import logging
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from pydantic import BaseModel, Field

app = FastAPI(title="AI Subject Line Generator")
logger = logging.getLogger(__name__)


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")

try:
    ai_client = genai.Client()
except Exception as exc:
    ai_client = None
    logger.exception("Gemini client initialization failed")


class GenerationRequest(BaseModel):
    topic: str = Field(max_length=500)
    tone: Literal["Professional", "Urgent", "Funny"]


@app.post("/generate-subjects")
async def generate_subject_lines(request: GenerationRequest):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be blank.",
        )
    if ai_client is None:
        raise HTTPException(
            status_code=503,
            detail="Gemini is unavailable. Configure GEMINI_API_KEY and restart the server.",
        )

    prompt = (
        "Generate 5 high-converting email subject lines. "
        f"Topic: {topic}. Tone: {request.tone}. "
        "Output a numbered list 1-5 only."
    )

    try:
        response = await ai_client.aio.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        return {"subject_lines": (response.text or "").strip()}
    except Exception as exc:
        logger.exception("Gemini subject line generation failed")
        raise HTTPException(
            status_code=502,
            detail="Subject generation failed. Please try again later.",
        ) from exc
