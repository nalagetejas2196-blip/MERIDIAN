# MERIDIAN — Teacher Code Walkthrough & Competition Script

## 1. Executive Summary & Problem Addressed
Most educational AI platforms act as generic chatbots: students paste homework, the model provides the code, and the student submits it without true comprehension. 
**MERIDIAN** addresses this with an unbending architectural distinction:
> **AI assistance can scaffold learning, but only unassisted, fresh assessments can verify independent mastery.**

---

## 2. Source Code Architecture & File Map

### Core System
- **Configuration & Identity:** [config.py](file:///C:/Users/nalag/.gemini/antigravity/scratch/meridian/backend/app/core/config.py)
  - Centrally stores product name, tagline, Ollama endpoints, and JWT security keys.
- **Relational Storage:** [entities.py](file:///C:/Users/nalag/.gemini/antigravity/scratch/meridian/backend/app/models/entities.py)
  - Tracks discrete skill states: `unassessed`, `needs_development`, `developing`, `demonstrated_assisted`, `demonstrated_independently`.
- **Assessment Service:** [assessment_service.py](file:///C:/Users/nalag/.gemini/antigravity/scratch/meridian/backend/app/services/assessment_service.py)
  - Deterministically scores submissions against rubrics. Ensures that any use of hints permanently caps the attempt status at `demonstrated_assisted`.

### AI, RAG & Expert System
- **Transparent Rule Engine:** [engine.py](file:///C:/Users/nalag/.gemini/antigravity/scratch/meridian/backend/app/rules_engine/engine.py)
  - Implements deterministic forward-chaining rules with priority conflict resolution and backward-chaining prerequisite proof trees.
- **Offline Semantic RAG:** [pipeline.py](file:///C:/Users/nalag/.gemini/antigravity/scratch/meridian/backend/app/rag/pipeline.py)
  - TF-IDF chunk indexing with cosine similarity, graduated hint templates (Levels 1-4), Ollama connection, and transparent fallback labeling.
- **Bounded Learning Agent:** [workflow.py](file:///C:/Users/nalag/.gemini/antigravity/scratch/meridian/backend/app/agent/workflow.py)
  - An 8-state finite state machine with allowlisted tools:
    1. `ASSESS_CURRENT_EVIDENCE`
    2. `IDENTIFY_PRIORITY_GAP`
    3. `CHECK_PREREQUISITES`
    4. `RETRIEVE_LEARNING_RESOURCES`
    5. `PROPOSE_LEARNING_TASK`
    6. `VALIDATE_ROLE_ALIGNMENT`
    7. `FINALIZE_RECOMMENDATION`
    8. `SCHEDULE_INDEPENDENT_VERIFICATION`

---

## 3. Syllabus Practicals Mapping (All 16 Implementations)
All algorithms are located in [practicals.py](file:///C:/Users/nalag/.gemini/antigravity/scratch/meridian/backend/app/algorithms/practicals.py) and verified in [test_core.py](file:///C:/Users/nalag/.gemini/antigravity/scratch/meridian/backend/tests/test_core.py):

| Practical # | Syllabus Topic | Function Name | Endpoint |
|---|---|---|---|
| Part A - 1 | Simple Reflex Agent | `run_simple_reflex_agent` | `/algorithms/practical/1` |
| Part A - 2 | Model-Based Agent | `run_model_based_agent` | `/algorithms/practical/2` |
| Part A - 3 | A* Search (8-Puzzle) | `run_astar_8puzzle` | `/algorithms/practical/3` |
| Part A - 4 | Alpha-Beta Pruning | `run_alphabeta_pruning` | `/algorithms/practical/4` |
| Part A - 5 | Tower of Hanoi | `run_tower_of_hanoi` | `/algorithms/practical/5` |
| Part A - 6 | Sudoku Solver (CSP) | `run_sudoku_solver` | `/algorithms/practical/6` |
| Part A - 7 | Local Beam Search (TSP) | `run_tsp_local_beam_search` | `/algorithms/practical/7` |
| Part B - 8 | BFS Planning | `run_bfs_planning` | `/algorithms/practical/8` |
| Part B - 9 | DFS Problem Solving | `run_dfs_problem_solving` | `/algorithms/practical/9` |
| Part B - 10 | 8-Queens Backtracking | `run_eight_queens` | `/algorithms/practical/10` |
| Part B - 11 | Rule-Based Chatbot | `run_rule_based_chatbot` | `/algorithms/practical/11` |
| Part B - 12 | Number Guessing Agent | `run_number_guessing_agent` | `/algorithms/practical/12` |
| Part B - 13 | Goal Stack Planning (STRIPS) | `run_goal_stack_planning` | `/algorithms/practical/13` |
| Part B - 14 | Minimax Game Agent | `run_minimax_tictactoe` | `/algorithms/practical/14` |
| Part C - 15 | Medical Diagnosis System | `run_medical_diagnosis_expert_system` | `/algorithms/practical/15` |
| Part C - 16 | Rule Recommendation System | `run_rule_based_recommendation_system` | `/algorithms/practical/16` |

---

## 4. Likely Teacher Questions and Defensible Answers

### Q1: "Why did you build your own rule engine instead of asking an LLM to decide what the student needs next?"
**Answer:** "LLMs are probabilistic and prone to hallucination or inconsistent decisions across requests. In an accredited educational system, prerequisite enforcement must be 100% deterministic, audit-traceable, and explainable. Our forward and backward chaining engine guarantees that if a rule matches, the exact same pedagogical decision is made every time with full provenance."

### Q2: "What prevents a student from cheating using the AI chat to pass assessments?"
**Answer:** "First, the Assessment Workbench is divided into two strict categories: Assisted Practice and Independent Verification. During an Independent Assessment, hints are disabled and the interface restricts assistance. Second, even in assisted mode, any hint usage permanently flags the database record as `demonstrated_assisted`, which triggers Rule 3 in our engine: mandating an unassisted reassessment before independent certification is granted."

### Q3: "How does the system operate without internet access or paid APIs?"
**Answer:** "MERIDIAN is built around zero mandatory cost. It uses SQLite for local relational storage, an in-process TF-IDF vector index for local textbook retrieval, and local Ollama (`llama3.2:3b`) for inference. If Ollama is turned off or unavailable, the system automatically falls back to a deterministic knowledge engine and clearly informs the user that it is in fallback mode."
