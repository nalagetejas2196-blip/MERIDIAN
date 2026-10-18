# MERIDIAN — Competition Presentation & Defense Script

## 1. 2-Minute Elevator Pitch
"Good morning, respected judges and professors.
Today, students frequently use AI chat tools to complete programming assignments. While AI can explain difficult concepts, students often copy solutions without gaining independent problem-solving skills.

We built **MERIDIAN: AI-Powered Skill Intelligence and Competency Verification Platform**.
Our core principle is:
> **AI can assist learning, but it must not be treated as proof that a student independently possesses a skill.**

MERIDIAN is built with a **strict zero-mandatory-cost policy**. It runs completely offline on standard student hardware using SQLite, an in-process semantic vector index, a deterministic forward/backward rule engine, an 8-state bounded agent, and all 16 AI syllabus practicals."

---

## 2. 5-Minute Live Interactive Demonstration Flow

### Minute 1: The Competency Matrix & Role Roadmap
1. Open the MERIDIAN Dashboard at `http://localhost:5173`.
2. Highlight the **Target Role Roadmap** selector. Switch between `Junior Python Developer` and `Junior Java Developer` to show dynamic curriculum adjustment.
3. Show the **Assessed Competency Matrix**. Note that skills are stored in discrete states (`unassessed`, `needs_development`, `developing`, `demonstrated_assisted`, `demonstrated_independently`).

### Minute 2: Assisted Practice vs. Independent Verification
1. Switch to the **Assessment Workbench**. Select `task_python_oop_assisted`.
2. Click **Request Graduated Hint**. Explain the graduated hint policy (Conceptual $\to$ Specific $\to$ Guided $\to$ Worked Example).
3. Submit the code. Show that because hints were used, the database assigns `demonstrated_assisted`.
4. Now select `task_python_oop_independent`. Note the banner: **STRICT UNASSISTED EVALUATION (Hints Disabled)**.
5. Emphasize to the examiners: *Independent certification cannot be unlocked until a student solves a fresh task without AI assistance.*

### Minute 3: Offline RAG with Source Citations
1. Open the **AI Assistant & RAG** tab. Ask: *"How do classes and inheritance work in Python?"*
2. Point out the citations: `[python_oop_guide.md - Chunk 1]`.
3. Explain that the semantic retrieval runs locally using TF-IDF and cosine similarity across our markdown knowledge base, connecting to local Ollama (`llama3.2:3b`) or falling back deterministically when offline without hallucination.

### Minute 4: The 8-State Bounded Agent & Rule Explorer
1. Open **Bounded Agent** and click **Execute Bounded Agent**.
2. Walk the judges through the 8 finite states and the tool calls (`db.get_student_evidence`, `rules.backward_chain_verify`, `rag.retrieve_local_chunks`). Explain why unbounded loops are prohibited.
3. Open **Rule Explorer** to demonstrate deterministic forward chaining, showing which rules fired, their priority scores, and the backward chaining prerequisite tree.

### Minute 5: Algorithm Lab (16 Syllabus Practicals)
1. Switch to **Algorithm Lab (16)**.
2. Select **Practical 3: A* Search (8-Puzzle)** and click **Execute Algorithm**. Point out the Manhattan Distance heuristic and expanded nodes trace.
3. Select **Practical 4: Alpha-Beta Pruning** to show tree evaluation and pruned branch reduction.
4. Select **Practical 10: 8-Queens Backtracking** or **Practical 13: Goal Stack Planning (STRIPS)** to demonstrate that all standard syllabus practicals are preserved, runnable, and test-verified.

---

## 3. Defense Questions & Defensible Answers

### Q: "Why not use LangChain or an open-ended autonomous agent like AutoGPT?"
**A:** "Autonomous loops with open-ended tools are unpredictable, can spin indefinitely, and consume excessive memory or tokens. In an educational evaluation platform, every recommendation step must have typed inputs, finite timeouts, deterministic bounds, and complete audit logging. Our bounded state machine gives full observability and guarantees execution termination."

### Q: "Can a student alter the database locally to fabricate independent mastery?"
**A:** "In a production academic deployment, the SQLite database resides on the department's authenticated evaluation server, while students interact via the authenticated web client using JWT tokens. For this competition prototype, it runs locally to prove zero-cost feasibility on student laptops without hosting fees."
