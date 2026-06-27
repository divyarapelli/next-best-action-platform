from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_context_agent(situation_text):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a customer context extractor. Respond ONLY with valid JSON. No markdown, no explanation, just JSON. Format exactly: { 'customer_name': 'string or Unknown', 'renewal_days': number or null, 'complaints': ['list', 'of', 'complaints'], 'competitor_mentioned': true or false, 'competitor_name': 'string or null', 'sentiment': 'positive' or 'neutral' or 'negative', 'key_topics': ['topic1', 'topic2'] }"
                },
                {"role": "user", "content": situation_text}
            ],
            temperature=0.1,
            max_tokens=500
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"Context agent error: {e}")
        return {"customer_name": "Unknown", "renewal_days": None, "complaints": [], "competitor_mentioned": False, "competitor_name": None, "sentiment": "neutral", "key_topics": []}
