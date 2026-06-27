from groq import Groq
import os
import json
from dotenv import load_dotenv
from backend.agents.rag_agent import run_rag_agent
from backend.agents.risk_agent import run_risk_agent
from backend.agents.context_agent import run_context_agent
from backend.memory.memory_store import get_similar_actions, get_memory_summary

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_planner(situation_text):
    try:
        context = run_context_agent(situation_text)
        risk = run_risk_agent(situation_text)
        rag_results = run_rag_agent(situation_text)
        memory_summary = get_memory_summary(situation_text)
        
        prompt = f"""
Customer Situation: {situation_text}

Extracted Context: {json.dumps(context)}

Risk Analysis: {json.dumps(risk)}

Relevant Playbook Rules:
{chr(10).join([r['content'] for r in rag_results])}

Memory of Past Decisions:
{memory_summary}

Generate exactly 3 Next Best Actions as JSON array.
Respond ONLY with valid JSON array. No markdown.
Each action must have:
- action_title: string
- reason: string  
- confidence: number 0-100
- evidence: string (which playbook rule)
- memory_influenced: true or false
"""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an intelligent Next Best Action engine. Always respond with valid JSON array only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        
        parsed_array = json.loads(response.choices[0].message.content)
        
        return {
            "recommendations": parsed_array,
            "planner_mode": "groq-llama3.3-70b",
            "risk_level": risk.get("risk_level") if risk else "UNKNOWN",
            "health_score": risk.get("health_score") if risk else 50,
            "health_label": risk.get("health_label") if risk else "Unknown",
            "urgency_score": risk.get("urgency_score") if risk else 5,
            "context": context if context else {},
            "rag_hits": len(rag_results) if rag_results else 0,
            "memory_hits": 1 if memory_summary and "similar" in memory_summary else 0
        }
    except Exception as e:
        raise RuntimeError(f"Groq planner failed: {e}")
