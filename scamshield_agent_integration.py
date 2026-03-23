"""
ScamShield Agent Integration — Groq API Version
=================================================
FastAPI server exposing ScamShield as a REST API.
Deploy on Render.com free tier — works 24/7.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from scamshield_agent_core import ScamShieldAgent
import base64
import io

app = FastAPI(
    title="ScamShield API",
    description="UK Scam Detection & Intelligence API — Powered by Groq",
    version="2.0.0"
)

# ── CORS — allows Netlify frontend to call this backend ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ScamShieldAgent()


# ── Request models ──

class ChatAnalysisRequest(BaseModel):
    chat_text: str
    user_name: Optional[str] = "there"

class QuestionRequest(BaseModel):
    question: str
    user_name: Optional[str] = "there"

class PlatformCheckRequest(BaseModel):
    platform_name: str
    user_name: Optional[str] = "there"

class InterrogationRequest(BaseModel):
    scam_type: str
    platform: Optional[str] = None
    user_name: Optional[str] = "there"

class RegionalRequest(BaseModel):
    city: str

class ImageOCRRequest(BaseModel):
    image_data: str
    media_type: Optional[str] = "image/jpeg"

class PDFExtractRequest(BaseModel):
    pdf_data: str
    user_name: Optional[str] = "there"


# ── Endpoints ──

@app.get("/")
def root():
    return {
        "name": "ScamShield UK API",
        "version": "2.0.0",
        "engine": "Groq llama-3.3-70b-versatile",
        "status": "active",
        "endpoints": [
            "/analyze-chat",
            "/ask",
            "/check-platform",
            "/interrogation-questions",
            "/regional-threat",
            "/extract-image-text",
            "/extract-pdf-text"
        ]
    }


@app.post("/analyze-chat")
def analyze_chat(request: ChatAnalysisRequest):
    if not request.chat_text or len(request.chat_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Chat text too short (minimum 20 characters)")
    result = agent.analyze_chat(chat_text=request.chat_text, user_name=request.user_name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    answer = agent.ask_question(question=request.question, user_name=request.user_name)
    return {"answer": answer, "user": request.user_name}


@app.post("/investigate")
def investigate_target(request: QuestionRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Target required")
    answer = agent.investigate(target=request.question)
    return {"answer": answer}


@app.post("/check-platform")
def check_platform(request: PlatformCheckRequest):
    if not request.platform_name:
        raise HTTPException(status_code=400, detail="Platform name required")
    assessment = agent.check_platform(platform_name=request.platform_name, user_name=request.user_name)
    return {"platform": request.platform_name, "assessment": assessment}


@app.post("/interrogation-questions")
def get_interrogation_questions(request: InterrogationRequest):
    questions = agent.generate_interrogation_questions(
        scam_type=request.scam_type,
        platform=request.platform,
        user_name=request.user_name
    )
    return {"scam_type": request.scam_type, "platform": request.platform, "questions": questions}


@app.post("/regional-threat")
def get_regional_threat(request: RegionalRequest):
    threat_info = agent.get_regional_threat(city=request.city)
    return {"city": request.city, "threat_intelligence": threat_info}


@app.post("/extract-image-text")
def extract_image_text(request: ImageOCRRequest):
    """Extract text from a screenshot using Groq vision."""
    if not request.image_data:
        raise HTTPException(status_code=400, detail="image_data is required")
    try:
        text = agent.extract_text_from_image(
            base64_image=request.image_data,
            media_type=request.media_type or "image/jpeg"
        )
        return {"success": True, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")


@app.post("/extract-pdf-text")
def extract_pdf_text(request: PDFExtractRequest):
    """Extract text from a PDF file uploaded as base64."""
    if not request.pdf_data:
        raise HTTPException(status_code=400, detail="pdf_data is required")
    try:
        from pypdf import PdfReader
        pdf_bytes = base64.b64decode(request.pdf_data)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF — it may be a scanned image")
        return {"success": True, "text": text, "pages": len(reader.pages)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
