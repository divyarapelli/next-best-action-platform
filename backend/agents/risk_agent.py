from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_risk_agent(situation_text):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a customer risk analyzer. Respond ONLY with valid JSON. No markdown, no explanation, just JSON. Format exactly: { 'risk_level': 'HIGH' or 'MEDIUM' or 'LOW', 'risk_reasons': ['reason1', 'reason2'], 'urgency_score': number between 1-10, 'health_score': number 0-100, 'health_label': 'Critical' or 'At Risk' or 'Healthy' } Health score rules: Start at 100. Subtract 40 if competitor mentioned. Subtract 25 if renewal within 15 days. Subtract 20 if negative sentiment. Subtract 15 if support complaints. Subtract 15 if low usage mentioned. Minimum 0. health_label: Critical if health_score < 30, At Risk if health_score < 60, Healthy if >= 60"
                },
                {"role": "user", "content": situation_text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"Risk agent error: {e}")
        return {"risk_level": "LOW", "risk_reasons": ["Analysis failed"], "urgency_score": 1, "health_score": 50, "health_label": "Unknown"}
