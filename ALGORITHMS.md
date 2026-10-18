# MERIDIAN Algorithm Lab Specification (16 Syllabus Practicals)

This document provides mathematical formulations, algorithmic logic, time/space complexity analysis, and verification references for all 16 AI Lab syllabus practicals implemented in MERIDIAN (`backend/app/algorithms/practicals.py`).

---

## PART A: SEARCH & HEURISTICS

### Practical 1: Simple Reflex Agent
- **Syllabus Category:** Intelligent Agents & Environments
- **Environment:** 2-Location Vacuum Cleaner World ($A, B$). Percept: $(location, status \in \{Clean, Dirty\})$.
- **Algorithm:** Condition-Action table lookup without internal state history:
  $$\text{Action} = \begin{cases} \text{Suck} & \text{if } status = \text{Dirty} \\ \text{Right} & \text{if } location = A \\ \text{Left} & \text{if } location = B \end{cases}$$
- **Complexity:** Time: $O(1)$ per step, Space: $O(1)$.
- **Inspection Route:** `/api/v1/algorithms/practical/1`

### Practical 2: Model-Based Reflex Agent
- **Syllabus Category:** Agent Architectures with Internal State
- **Mechanism:** Maintains an internal state model $\mathcal{M} = \{A: status, B: status\}$. Updates model with every percept. Halts cleanly ($\text{NoOp}$) once all rooms are verified clean.
- **Complexity:** Time: $O(1)$ per step, Space: $O(|\text{locations}|)$.
- **Inspection Route:** `/api/v1/algorithms/practical/2`

### Practical 3: A* Search for the 8-Puzzle
- **Syllabus Category:** Informed / Heuristic Search
- **Evaluation Function:** $f(n) = g(n) + h(n)$, where $g(n)$ is actual path cost from start, and $h(n)$ is the Manhattan Distance:
  $$h(n) = \sum_{i=1}^{8} |r_{\text{curr}}(i) - r_{\text{goal}}(i)| + |c_{\text{curr}}(i) - c_{\text{goal}}(i)|$$
- **Properties:** Admissible ($h(n) \le h^*(n)$) and Consistent ($h(n) \le c(n, a, n') + h(n')$), guaranteeing optimal solution path.
- **Complexity:** Time: $O(b^d)$, Space: $O(b^d)$.
- **Inspection Route:** `/api/v1/algorithms/practical/3`

### Practical 4: Alpha-Beta Pruning
- **Syllabus Category:** Adversarial Search in Zero-Sum Games
- **Mechanism:** Minimax depth-first search maintaining bounds $\alpha$ (highest score guaranteed to maximizer) and $\beta$ (lowest score guaranteed to minimizer). Prunes branches when $\beta \le \alpha$.
- **Complexity:** Best-case Time: $O(b^{d/2})$, Space: $O(bd)$.
- **Inspection Route:** `/api/v1/algorithms/practical/4`

### Practical 5: Tower of Hanoi
- **Syllabus Category:** Problem Solving & Divide-and-Conquer
- **Recurrence Relation:** $T(n) = 2T(n-1) + 1$, yielding exactly $2^n - 1$ optimal moves.
- **Complexity:** Time: $O(2^n)$, Space: $O(n)$ call stack depth.
- **Inspection Route:** `/api/v1/algorithms/practical/5?param=3`

### Practical 6: Sudoku Solver using CSP Backtracking
- **Syllabus Category:** Constraint Satisfaction Problems (CSP)
- **Constraints:** All row elements, column elements, and $3 \times 3$ sub-grid elements must be unique in $\{1, \dots, 9\}$.
- **Algorithm:** Depth-first recursive assignment with forward constraint checking.
- **Complexity:** Time: $O(9^{m})$ where $m$ is number of empty cells, Space: $O(81)$.
- **Inspection Route:** `/api/v1/algorithms/practical/6`

### Practical 7: Local Beam Search for Travelling Salesperson Problem (TSP)
- **Syllabus Category:** Local & Heuristic Search
- **Mechanism:** Retains a beam of $k$ candidate complete tours. In each iteration, generates all 2-opt neighbor permutations across the beam, sorts by total Euclidean distance, and retains the top $k$ candidates.
- **Complexity:** Time: $O(\text{iterations} \cdot k \cdot n^2)$, Space: $O(k \cdot n)$.
- **Inspection Route:** `/api/v1/algorithms/practical/7?param=3`

---

## PART B: SYSTEMATIC SEARCH, PLANNING & AGENTS

### Practical 8: Breadth-First Search (BFS) Planning
- **Syllabus Category:** Uninformed Search
- **Data Structure:** FIFO Queue.
- **Properties:** Guarantees shortest path in unweighted graphs.
- **Complexity:** Time: $O(V + E)$, Space: $O(V)$.
- **Inspection Route:** `/api/v1/algorithms/practical/8`

### Practical 9: Depth-First Search (DFS) Problem Solving
- **Syllabus Category:** Uninformed Search & Backtracking
- **Data Structure:** LIFO Stack (call stack recursion).
- **Properties:** Explores deepest paths first; low memory footprint.
- **Complexity:** Time: $O(V + E)$, Space: $O(\text{depth})$.
- **Inspection Route:** `/api/v1/algorithms/practical/9`

### Practical 10: 8-Queens using Backtracking
- **Syllabus Category:** Backtracking & State Space Reduction
- **Constraint Representation:** Vector $Q$ of length $n$, where $Q[i]$ is the column for queen in row $i$. Safety condition:
  $$Q[i] \neq Q[j] \quad \text{and} \quad |Q[i] - Q[j]| \neq |i - j| \quad (\forall j < i)$$
- **Complexity:** Time: $O(n!)$, Space: $O(n)$.
- **Inspection Route:** `/api/v1/algorithms/practical/10?param=8`

### Practical 11: Rule-Based Chatbot
- **Syllabus Category:** Natural Language Understanding & Pattern Matching
- **Mechanism:** Deterministic regex intent matchers bound to pedagogical response templates.
- **Complexity:** Time: $O(R \cdot L)$ where $R$ is rules and $L$ is token length.
- **Inspection Route:** `/api/v1/algorithms/practical/11?param=What+is+RAG`

### Practical 12: Number-Guessing Binary Search Agent
- **Syllabus Category:** Optimal Search Under Monotonic Feedback
- **Strategy:** Repeatedly bisects interval $[L, R]$ with query $M = \lfloor (L + R) / 2 \rfloor$.
- **Complexity:** Worst-case iterations: $\lceil \log_2(N) \rceil \le 7$ for range $[1, 100]$.
- **Inspection Route:** `/api/v1/algorithms/practical/12?param=42`

### Practical 13: Goal Stack Planning (STRIPS)
- **Syllabus Category:** Classical Automated Planning
- **Domain:** Blocks World with predicates: $\text{ON}(x, y), \text{ONTABLE}(x), \text{CLEAR}(x), \text{HOLDING}(x), \text{ARMEMPTY}$.
- **Mechanism:** Pushes goal onto stack; satisfies preconditions recursively via operators ($\text{STACK}, \text{UNSTACK}, \text{PICKUP}, \text{PUTDOWN}$).
- **Inspection Route:** `/api/v1/algorithms/practical/13`

### Practical 14: Minimax Game Agent (Tic-Tac-Toe)
- **Syllabus Category:** Game Theory & Adversarial Search
- **Payoff Matrix:** $+10$ (AI Win), $-10$ (Adversary Win), $0$ (Draw).
- **Properties:** Mathematically guarantees at least a draw against any player.
- **Complexity:** Time: $O(9!)$, Space: $O(9)$ depth.
- **Inspection Route:** `/api/v1/algorithms/practical/14`

---

## PART C: EXPERT SYSTEMS & RECOMMENDATIONS

### Practical 15: Medical Diagnosis Expert System
- **Syllabus Category:** Rule-Based Expert Systems & Certainty Factors
- **Mechanism:** Backward-chaining pattern matcher comparing patient symptom vectors against synthetic diagnostic rules.
- **Academic Disclaimer:** Synthetic simulation for educational purposes only; strictly disclaims clinical diagnosis.
- **Inspection Route:** `/api/v1/algorithms/practical/15?param=cough,runny_nose,sneezing`

### Practical 16: Rule-Based Recommendation System
- **Syllabus Category:** Applied Expert Systems
- **Integration:** Directly aligns with MERIDIAN's internal pedagogical rule engine, demonstrating how priority rules map assessed weaknesses into actionable learning pathways.
- **Inspection Route:** `/api/v1/algorithms/practical/16`
