# MERIDIAN
## AI-Powered Skill Intelligence and Competency Verification Platform

> **Tagline:** Learn intelligently. Demonstrate independently.
> **Mission:** Help students identify skill gaps for a chosen technical role, practise with AI-assisted guidance, and demonstrate their actual understanding through new independent assessments.
> **Core Principle:** AI can assist learning, but it must not be treated as proof that a student independently possesses a skill.

---

### Key Architectural Characteristics
- **Zero Mandatory Cost Policy:** Runs completely locally on Windows with 16 GB RAM and integrated graphics. No paid OpenAI, Anthropic, or cloud API keys required.
- **Explainable Rule Engine:** Deterministic forward and backward chaining expert system with conflict resolution and complete provenance tracing.
- **Local RAG Pipeline:** Offline document indexing with cosine similarity retrieval, graduated hints (1 to 4), and local Ollama (`llama3.2:3b`) inference with automatic deterministic fallback.
- **Bounded Learning Agent:** Finite state workflow (8 observable steps) with typed contracts and strictly allowlisted tools.
- **Algorithm Lab (16 Practicals):** Runnable, interactive implementations and tests for all 16 AI Lab syllabus practicals across Parts A, B, and C.

---

### Project Structure
```
meridian/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── core/                    # Config, DB session, JWT security
│   │   ├── models/                  # SQLAlchemy ORM entities
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   ├── services/                # Assessment & seed services
│   │   ├── rules_engine/            # Forward/backward expert system
│   │   ├── rag/                     # TF-IDF local retrieval & Ollama
│   │   ├── agent/                   # 8-state bounded workflow agent
│   │   └── algorithms/              # 16 syllabus practical algorithms
│   ├── tests/
│   │   └── test_core.py             # 5 comprehensive pytest suites
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx                  # Single-page application console
│   │   ├── api.ts                   # Typed API client
│   │   └── index.css                # Slate & teal accessible styling
│   ├── package.json
│   └── vite.config.ts
├── data/
│   └── knowledge_base/              # Grounded markdown textbooks
└── docs/
    ├── API_GUIDE.md
    ├── TEACHER_CODE_WALKTHROUGH.md
    ├── PROJECT_LIMITATIONS.md
    └── COMPETITION_PRESENTATION.md
```

---

### Windows Setup & Execution Instructions

#### 1. Backend Setup & Run
Open PowerShell in `meridian/backend`:
```powershell
# Install dependencies
python -m pip install -r requirements.txt
python -m pip install "pydantic[email]"

# Run test suite
python -m pytest tests/ -v

# Launch FastAPI server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### 2. Frontend Setup & Run
Open a second PowerShell window in `meridian/frontend`:
```powershell
npm install
npm run dev
```
Navigate to `http://localhost:5173` in your browser.

#### 3. Default Demo Credentials
- **Student Account:** `student_demo` / `meridian2026`
- **Instructor Account:** `prof_admin` / `examiner2026`

#### 4. Optional Local Ollama LLM
If you wish to enable the local LLM instead of the deterministic knowledge engine fallback:
```powershell
ollama run llama3.2:3b
```
Meridian automatically queries `http://localhost:11434` and falls back gracefully when Ollama is offline.
