# 🧠 Intelligent Next Best Action Platform
### **Submission for XLVentures.AI Hackathon 2026**

![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3%2070B-orange)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Python](https://img.shields.io/badge/Python-3.10+-blue)

An AI-powered decision support system for B2B SaaS Customer Success teams that analyzes raw customer interactions, evaluates churn risk, retrieves company playbooks via RAG, consults historical action memory, and recommends structured Next Best Actions with a Human-in-the-Loop feedback loop.

---

## 🗺️ The Google Maps Analogy
Managing B2B accounts can feel like driving in unfamiliar territory. This platform acts as **Google Maps for Customer Success Managers (CSMs)**:
* **The Coordinates:** The raw CRM interaction notes or emails represent your current vehicle position.
* **The Hazards:** The **Risk Agent** checks for speed traps, road closures, or bad weather (churn warning signs).
* **The Route Rules:** The **RAG Agent** reads the road signs and highway code (Company Playbooks) to ensure compliance.
* **Past Driver History:** The **Memory Store** checks how past drivers handled this exact stretch of road.
* **The Next Turn:** The **Planner Agent** calculates the optimal route and says *"In 500 feet, turn left"* (Next Best Actions).
* **The Driver in the Loop:** The CSM still holds the steering wheel. They can accept or override the guidance (Approve/Reject), which immediately updates the map's traffic data for the next driver (SQLite memory).

---

## ⚙️ How It Works (6 Simple Steps)
1. **Pasting Interactions:** The CSM paste meeting notes, emails, or call transcripts into the dashboard.
2. **Fact & Context Extraction:** The **Context Agent** parses key details such as the company name, renewal countdown, specific complaints, and customer sentiment.
3. **Risk & Urgency Scoring:** The **Risk Agent** uses Groq LLaMA 3.3 70B to classify churn risk (HIGH/MEDIUM/LOW), list risk factors, and score urgency on a scale of 1–10.
4. **Semantic Playbook Search (RAG):** The **RAG Agent** queries a ChromaDB vector database containing company playbooks to retrieve exact rules for the situation.
5. **Memory Retrieval:** The system retrieves similar past customer scenarios and their outcomes from the SQLite database.
6. **Synthesis & Human Review:** The **Planner Agent** fuses all the insights into 3 ranked recommendations. The CSM approves or rejects each action, logging their decision to retrain the memory system.

---

## 🏗️ System Architecture

```
                       +-------------------------------+
                       |   Raw Customer Interaction    |
                       +---------------+---------------+
                                       |
                                       v
                       +---------------+---------------+
                       |     Central Planner Agent     |
                       +---------------+---------------+
                                       |
       +-------------------------------+-------------------------------+----------+
       |                               |                                          |
       v                               v                                          v
+------+-------+               +-------+-------+-------+               +-------+-------+-------+
|  RAG Agent   |               |  Risk Agent           |               | Context Agent         |
| (ChromaDB)   |               | (Groq LLaMA 3.3 70B)  |               | (Groq LLaMA 3.3 70B)  |
+------+-------+               +-------+-------+                         +-------+-------+
       |                               |                                          |
       +-------------------------------+-------------------------------+----------+
                                       |
                                       v
                       +---------------+---------------+
                       |  Synthesizer (Groq LLaMA 3.3 70B)     |
                       +---------------+---------------+
                                       |
                                       v
                       +---------------+---------------+
                       |  3 Ranked Next Best Actions   |
                       +---------------+---------------+
                                       |
                                       v
                       +---------------+---------------+
                       |      Human-in-the-Loop        |
                       |    (Approve / Reject UI)      |
                       +---------------+---------------+
                                       |
                                       v
                       +---------------+---------------+
                       |   SQLite Action Memory Store  |
                       +-------------------------------+
```

---

## 🛠️ Tech Stack

| Technology | Layer | Purpose |
|---|---|---|
| **Python 3.10+** | Core Language | Foundation of backend services and agents |
| **FastAPI** | Backend | High-performance REST API with CORS enablement |
| **Streamlit** | Frontend UI | Clean, dual-column dashboard for CSM workflows |
| **ChromaDB** | Vector DB | Persistent semantic indexing of `.txt` playbook rules |
| **SQLite + SQLAlchemy** | Relational DB | Local transaction history and action memory storage |
| **Groq LLaMA 3.3 70B** | LLM Engine | Ultra-fast inference powering Context, Risk, and Planner Agents via Groq API |
| **Pydantic** | Schema Validation | Ensures structured data contracts across endpoints |

---

## 🚀 Setup & Installation

### 1. Clone & Set Up Directory
```bash
git clone https://github.com/your-username/next-best-action-platform.git
cd next-best-action-platform
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root folder:
```env
GROQ_API_KEY=your_groq_api_key_here
CHROMA_DB_PATH=./chroma_db
SQLITE_DB_PATH=./memory/actions.db
PLAYBOOKS_PATH=./data/playbooks
```

### 4. Seed Playbooks & Run Ingestion
Add your playbook `.txt` files (e.g. `competitor_playbook.txt`, `renewal_playbook.txt`, `support_playbook.txt`) into `./data/playbooks/` and run ingestion to build the vector index:
```bash
python -m backend.knowledge_base.ingest
```

### 5. Start Backend Server (FastAPI)
```bash
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

### 6. Start Frontend Dashboard (Streamlit)
Open a new terminal window:
```bash
streamlit run frontend/app.py
```

---

## 💡 Demo Scenarios

### Scenario A: Churn & Competitor Risk at Renewal
* **Input Text:** 
  > *"Had a call with Acme Corp today. They mentioned their renewal is coming up in 20 days. The champion sounded frustrated because they have two unresolved high-priority bugs open. She mentioned that they are evaluating Gainsight to see if they offer more responsive support."*
* **Expected Output:**
  * **Risk:** `HIGH`
  * **Actions Recommended:**
    1. Escalate the unresolved bugs to Engineering immediately (from Support Playbook).
    2. Arrange a QBR/value review with the key stakeholders to highlight past ROI (from Renewal Playbook).
    3. Shift conversation to migration costs and total cost of ownership (from Competitor Playbook).

### Scenario B: Missing Feature / Price Match Discussion
* **Input Text:**
  > *"Spoke to Delta Systems. They liked our recent demo but forwarded a competitor pricing sheet. They asked if we could match their lower price, and also complained that we lack the automated reporting module they need."*
* **Expected Output:**
  * **Risk:** `MEDIUM`
  * **Actions Recommended:**
    1. Conduct a TCO calculation showing transition costs instead of discounting (from Competitor Playbook).
    2. Discover and document the use case behind the automated reporting feature (from Competitor Playbook).
    3. Loop in the Account Executive to negotiate value-based terms (from Competitor Playbook).

---

# Evaluation Criteria Coverage

| Criterion | How We Address It |
|---|---|
| **AI Capabilities** | Implements a robust multi-agent pattern with specialized extraction, classification, and planning roles. Prompts enforce strict JSON schemas for predictable programmatic ingestion. |
| **Business Impact** | Directly targets SaaS churn prevention and upselling. Fuses operational data (renewals, support tickets, competitor threats) into actionable plays for front-line CSMs. |
| **Technical Design** | Decoupled agent architecture, fast semantic retrieval via ChromaDB vector indexing, and persistent relational memory. Highly performant REST endpoints using FastAPI. |
| **Human in the Loop** | Gives human agents final veto power. Decisions are logged directly to the system's SQLite memory, showing a continuous pathway to model-refinement. |
