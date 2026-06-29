"""
app.py — FastAPI backend for the Next Best Action platform.
Exposes endpoints for analysis, feedback, and action history.
"""

import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel

from backend.agents.planner_agent import run_planner
from backend.agents.risk_agent import run_risk_agent
from backend.agents.context_agent import run_context_agent
from backend.memory.memory_store import init_db, save_action, get_all_history, get_confidence_trend

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ─── Lifespan: initialize DB on startup ─────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the actions table on startup if it doesn't exist."""
    init_db()
    yield


app = FastAPI(title="Next Best Action Platform", version="1.0.0", lifespan=lifespan)

# ─── CORS: allow Streamlit and local frontends to connect ────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request / Response Models ───────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    interaction: str  # Raw meeting notes or customer interaction text
    domain: str = "Customer Success"  # Business domain


class FeedbackRequest(BaseModel):
    action_title: str       # The recommended action
    situation: str          # Brief situation summary
    confidence: float       # Confidence score (0-100)
    decision: str           # "approved" or "rejected"
    domain: str = "Customer Success"  # Business domain


class GenerateEmailRequest(BaseModel):
    action_title: str       # The approved action
    situation: str          # Original interaction text
    domain: str = "Customer Success"  # Business domain


# ─── POST /analyze ───────────────────────────────────────────────────────────────

@app.post("/analyze")
def analyze_interaction(req: AnalyzeRequest):
    """
    Run the full agent pipeline on customer interaction text.
    Returns recommendations, risk assessment, and extracted context.
    """
    print("ENTER /analyze")
    try:
        result = run_planner(req.interaction)
        print("EXIT /analyze")
        return result
    except Exception as exc:
        print(f"ERROR /analyze: {exc}")
        raise


# ─── POST /feedback ──────────────────────────────────────────────────────────────

@app.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    """
    Save a CSM's decision (approved/rejected) on a recommended action.
    Stores the record in SQLite for future memory-based retrieval.
    """
    save_action(
        situation=req.situation,
        action=req.action_title,
        confidence=req.confidence,
        decision=req.decision,
    )
    return {"status": "saved"}


# ─── GET /history ────────────────────────────────────────────────────────────────

@app.get("/history")
def get_history():
    """Return the last 10 recorded actions from memory."""
    print("ENTER /history")
    try:
        result = get_all_history()
        print("EXIT /history")
        return result
    except Exception as exc:
        print(f"ERROR /history: {exc}")
        raise


# ─── POST /generate-email ─────────────────────────────────────────────────────────

@app.post("/generate-email")
def generate_email(req: GenerateEmailRequest):
    """
    Generate a professional email draft based on the approved action and situation.
    Uses Groq Llama 3.3 to create a concise, specific email with subject line.
    """
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional customer success email writer. Respond ONLY with valid JSON. No markdown. Format: { 'subject': 'email subject line', 'body': 'full email body under 120 words' } Rules: - Professional but warm tone - Specific to the situation - Clear next step at the end - Sign off as 'Your Customer Success Team'"
                },
                {
                    "role": "user",
                    "content": f"Action: {req.action_title}\nSituation: {req.situation}\nDomain: {req.domain}"
                }
            ],
            temperature=0.3,
            max_tokens=400
        )
        
        raw_content = response.choices[0].message.content
        print(f"Groq raw response: {raw_content[:500]}")
        
        # Try to parse JSON, strip markdown if present
        content = raw_content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        print(f"After stripping: {content[:500]}")
        
        # Use demjson3 to handle single-quoted JSON
        try:
            import demjson3
            result = demjson3.decode(content)
        except ImportError:
            # Fallback: replace single quotes with double quotes (carefully)
            import re
            content = re.sub(r"'([^']*)':", r'"\1":', content)  # keys
            content = re.sub(r": '([^']*)'", r': "\1"', content)  # values
            result = json.loads(content)
        
        return {"subject": result["subject"], "body": result["body"]}
        
    except Exception as exc:
        print(f"Email generation error: {exc}")
        raise


# ─── GET /confidence-trend ───────────────────────────────────────────────────────

@app.get("/confidence-trend")
def get_confidence_trend_endpoint():
    """
    Return the last 20 approved actions with confidence scores ordered by timestamp.
    Used to plot confidence trend over time in the analytics dashboard.
    """
    print("ENTER /confidence-trend")
    try:
        result = get_confidence_trend()
        print("EXIT /confidence-trend")
        return result
    except Exception as exc:
        print(f"ERROR /confidence-trend: {exc}")
        raise
