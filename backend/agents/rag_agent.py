"""RAG agent for playbook retrieval."""

from backend.knowledge_base.ingest import search_knowledge


def run_rag_agent(situation_text: str) -> list[dict]:
    print("ENTER run_rag_agent")
    try:
        results = search_knowledge(situation_text)[:3]
        if not results:
            print("Warning: no RAG results found for the given situation.")
            print("EXIT run_rag_agent")
            return []
        result = [
            {"content": item["text"], "source_file": item["source"], "relevance_score": round(1.0 - (index * 0.1), 2)}
            for index, item in enumerate(results)
        ]
        print("EXIT run_rag_agent")
        return result
    except Exception as exc:
        print(f"RAG agent error: {exc}")
        print("Using empty RAG results")
        return []
