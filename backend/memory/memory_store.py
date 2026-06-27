"""SQLite-backed memory store for past actions."""

import os
import re
from collections import Counter
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine, desc, or_
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DB_PATH = os.getenv("SQLITE_DB_PATH", "./memory/actions.db")
Base = declarative_base()


class Action(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    situation_summary = Column(String, nullable=False)
    action_taken = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    decision = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def save_action(situation: str, action: str, confidence: float, decision: str):
    session = SessionLocal()
    try:
        session.add(Action(situation_summary=situation, action_taken=action, confidence=confidence, decision=decision))
        session.commit()
    finally:
        session.close()


def get_similar_actions(situation_text: str):
    print("ENTER get_similar_actions")
    keywords = [word for word in re.findall(r"\w+", situation_text.lower()) if len(word) > 2]
    session = SessionLocal()
    try:
        query = session.query(Action)
        if keywords:
            query = query.filter(or_(*[Action.situation_summary.ilike(f"%{word}%") for word in keywords]))
        rows = query.order_by(desc(Action.timestamp)).limit(5).all()
        result = [{"id": row.id, "situation": row.situation_summary, "action": row.action_taken, "confidence": row.confidence, "decision": row.decision, "timestamp": row.timestamp.isoformat()} for row in rows]
        print(f"EXIT get_similar_actions with {len(result)} results")
        return result
    finally:
        session.close()


def get_memory_summary(situation_text: str):
    matches = get_similar_actions(situation_text)
    if not matches:
        return "No similar past actions found."
    counts = Counter((item["action"], item["decision"]) for item in matches)
    parts = [f"{action} was {decision} {count} time{'s' if count != 1 else ''}." for (action, decision), count in counts.items()]
    return f"In {len(matches)} similar past situations: " + " ".join(parts)


def get_all_history():
    session = SessionLocal()
    try:
        rows = session.query(Action).order_by(desc(Action.timestamp)).limit(10).all()
        return [{"id": row.id, "situation": row.situation_summary, "action": row.action_taken, "confidence": row.confidence, "decision": row.decision, "timestamp": row.timestamp.isoformat()} for row in rows]
    finally:
        session.close()


def get_confidence_trend():
    """Query last 20 approved actions ordered by timestamp ascending."""
    session = SessionLocal()
    try:
        rows = session.query(Action).filter(Action.decision == "approved").order_by(Action.timestamp.asc()).limit(20).all()
        return [
            {
                "timestamp": row.timestamp.isoformat(),
                "action_taken": row.action_taken,
                "confidence": row.confidence,
                "decision": row.decision
            }
            for row in rows
        ]
    finally:
        session.close()
