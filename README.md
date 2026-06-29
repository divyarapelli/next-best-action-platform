# 🧠 Intelligent Next Best Action Platform
### **Submission for XLVentures.AI Hackathon 2026**

![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3%2070B-orange)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Python](https://img.shields.io/badge/Python-3.10+-blue)

---

## 📋 Team Information

### Team Name
**[Team Name Placeholder]**

### Team Members
- **[Member 1 Name]** - [Role]
- **[Member 2 Name]** - [Role]
- **[Member 3 Name]** - [Role]
- **[Member 4 Name]** - [Role]

---

## 📌 Project Title
**Intelligent Next Best Action Platform**

---

## 🎯 Problem Statement
B2B SaaS Customer Success teams struggle with:
- **Information Overload:** Customer interactions across emails, calls, and tickets create fragmented data
- **Inconsistent Decision Making:** Different CSMs handle similar situations differently
- **Missed Churn Signals:** Early warning signs go unnoticed until it's too late
- **Playbook Compliance:** Company best practices exist but aren't consistently applied
- **Knowledge Silos:** Valuable lessons from past interactions aren't systematically reused

This platform solves these challenges by using AI to analyze customer interactions, assess risk, retrieve relevant playbooks, and recommend data-driven Next Best Actions with human oversight.

---

## ✨ Features

### Core Capabilities
- **Multi-Agent AI System:** Specialized agents for context extraction, risk analysis, and action planning
- **Real-time Risk Assessment:** Churn risk scoring (HIGH/MEDIUM/LOW) with urgency metrics
- **RAG-Powered Playbook Retrieval:** Semantic search across company playbooks using ChromaDB
- **Historical Memory System:** SQLite-based storage of past decisions for continuous learning
- **Human-in-the-Loop:** CSM approval/rejection workflow with feedback logging
- **Email Generation:** AI-powered email draft generation for approved actions
- **Export Reports:** Downloadable analysis reports for documentation

### Key Metrics
- **Health Score:** 0-100 customer health assessment
- **Urgency Score:** 1-10 priority ranking
- **Confidence Levels:** 0-100% recommendation confidence
- **RAG Hits:** Number of relevant playbook rules retrieved
- **Memory Hits:** Number of similar past scenarios found

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

## 🏗️ Architecture

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

## 🔄 Workflow

### Step-by-Step Process
1. **Input:** CSM pastes customer interaction text (meeting notes, emails, call transcripts)
2. **Context Extraction:** AI parses customer name, renewal days, complaints, sentiment, key topics
3. **Risk Analysis:** AI evaluates churn risk level, health score, urgency score
4. **Playbook Retrieval:** RAG searches ChromaDB for relevant playbook rules
5. **Memory Lookup:** System retrieves similar past scenarios and outcomes
6. **Action Planning:** AI synthesizes all inputs into 3 ranked Next Best Actions
7. **Human Review:** CSM approves or rejects each recommendation
8. **Feedback Loop:** Decisions logged to SQLite for continuous learning
9. **Email Generation:** AI drafts professional email for approved actions
10. **Export:** CSM can download analysis report

---

## 📸 Screenshots

### Dashboard View
- Input panel for customer interactions
- Risk assessment display with health metrics
- Recommended actions with confidence scores
- Approval/rejection buttons

### Analysis Results
- Risk level badge (HIGH/MEDIUM/LOW)
- Health score gauge (0-100)
- Urgency score indicator
- RAG knowledge hits count
- Memory hits count

### Email Generation
- Subject line preview
- Email body preview
- Copy/download options

---

## 🔗 GitHub Repository
https://github.com/divyarapelli/next-best-action-platform

---

## 🚀 Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/divyarapelli/next-best-action-platform.git
cd next-best-action-platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root folder:
```env
GROQ_API_KEY=your_groq_api_key_here
CHROMA_DB_PATH=./chroma_db_v2
SQLITE_DB_PATH=./memory/actions.db
PLAYBOOKS_PATH=./data/playbooks
MODEL_NAME=llama-3.3-70b-versatile
```

### 5. Seed Playbooks
Add your playbook `.txt` files (e.g. `competitor_playbook.txt`, `renewal_playbook.txt`, `support_playbook.txt`) into `./data/playbooks/` and run ingestion:
```bash
python -m backend.knowledge_base.ingest
```

### 6. Start Backend Server
```bash
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

### 7. Start Frontend Dashboard
Open a new terminal window:
```bash
streamlit run frontend/app.py
```

### 8. Access Application
Open http://localhost:8501 in your browser

---

## 🔮 Future Improvements

### Planned Enhancements
- **Multi-language Support:** Expand beyond English for global teams
- **Integration Hub:** Connect to CRM systems (Salesforce, HubSpot)
- **Advanced Analytics:** Dashboard with churn prediction trends
- **Mobile App:** iOS/Android app for on-the-go CSMs
- **Voice Input:** Speech-to-text for call transcript analysis
- **Collaborative Features:** Team notes and shared playbooks
- **A/B Testing:** Test different action recommendations
- **Custom Models:** Fine-tune models on company-specific data
- **Real-time Alerts:** Proactive notifications for high-risk accounts
- **API for Developers:** Enable third-party integrations

### Technical Enhancements
- **Caching Layer:** Redis for faster response times
- **Rate Limiting:** Protect API endpoints
- **Authentication:** OAuth2/JWT for secure access
- **Monitoring:** Prometheus/Grafana for system health
- **Testing:** Comprehensive unit and integration tests
- **CI/CD Pipeline:** Automated testing and deployment
