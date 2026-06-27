"""
ingest.py — Loads playbook .txt files into ChromaDB for RAG retrieval.
Splits documents into overlapping chunks and indexes them for semantic search.
"""

import os
import glob

import chromadb
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
PLAYBOOKS_PATH = os.getenv("PLAYBOOKS_PATH", "./data/playbooks")
COLLECTION_NAME = "playbooks"


# ─── Text Chunking ──────────────────────────────────────────────────────────────

def _split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into chunks of `chunk_size` characters with `overlap`
    characters shared between consecutive chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# ─── ChromaDB Client ────────────────────────────────────────────────────────────

def _get_collection():
    """Return (or create) the playbooks ChromaDB collection."""
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


# ─── Ingestion ───────────────────────────────────────────────────────────────────

def ingest_all_playbooks():
    """
    Load every .txt file from the playbooks folder, split into chunks,
    and upsert them into the ChromaDB 'playbooks' collection.
    Uses ChromaDB's built-in default embeddings (all-MiniLM-L6-v2).
    Only runs if collection is empty to avoid repeated ingestion.
    """
    collection = _get_collection()
    
    # Check if collection already has data
    try:
        count = collection.count()
        if count > 0:
            print(f"Collection already has {count} chunks. Skipping ingestion.")
            return
    except Exception as exc:
        print(f"Could not check collection count: {exc}. Proceeding with ingestion.")

    # Find all .txt playbook files
    pattern = os.path.join(PLAYBOOKS_PATH, "*.txt")
    files = glob.glob(pattern)

    if not files:
        print(f"WARNING: No .txt files found in {PLAYBOOKS_PATH}")
        return

    all_docs, all_ids, all_meta = [], [], []

    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Split file content into overlapping chunks
        chunks = _split_text(content, chunk_size=500, overlap=50)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{filename}__chunk_{i}"
            all_docs.append(chunk)
            all_ids.append(chunk_id)
            all_meta.append({"source": filename, "chunk_index": i})

    # Upsert all chunks into ChromaDB (idempotent — safe to re-run)
    collection.upsert(documents=all_docs, ids=all_ids, metadatas=all_meta)
    print(f"SUCCESS: Ingested {len(all_docs)} chunks from {len(files)} playbook(s)")


# ─── Search ──────────────────────────────────────────────────────────────────────

def search_knowledge(query: str, n_results: int = 3) -> list[dict]:
    """
    Search the playbooks collection for chunks most relevant to the query.
    Returns a list of dicts with 'text', 'source', and 'chunk_index'.
    """
    print(f"ENTER search_knowledge with query: {query[:50]}...")
    collection = _get_collection()
    results = collection.query(query_texts=[query], n_results=n_results)

    matched = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        matched.append({
            "text": doc,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
        })
    print(f"EXIT search_knowledge with {len(matched)} results")
    return matched


# ─── CLI Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ingest_all_playbooks()
