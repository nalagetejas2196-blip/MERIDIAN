# MERIDIAN REST API Reference Specification (v1)

Base URL: `http://localhost:8000/api/v1`
Interactive Swagger Docs: `http://localhost:8000/api/v1/docs`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Creates a new student account.
- **Request Body:**
  ```json
  {
    "email": "student@meridian.edu",
    "username": "student_user",
    "password": "secure_password",
    "full_name": "Student Name",
    "target_role": "Junior Python Developer"
  }
  ```
- **Response (200 OK):** User object without hashed password.

### `POST /auth/login`
Authenticates a user and returns a signed JWT access token.
- **Request Body:**
  ```json
  {
    "username_or_email": "student_demo",
    "password": "meridian2026"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { ... }
  }
  ```

### `GET /auth/me`
Retrieves current authenticated profile. Requires `Authorization: Bearer <token>`.

### `PUT /auth/target-role`
Updates the student's target technical role.
- **Query Parameter:** `role_name` (e.g., `Junior Java Developer`).

---

## 2. Assessment & Evidence Endpoints

### `GET /skills/evidence`
Retrieves all persistent skill mastery records for the authenticated student.
- **Response Items:**
  ```json
  {
    "id": 1,
    "skill_id": "python_basics",
    "skill_name": "Python Syntax & Control Flow",
    "status": "demonstrated_independently",
    "mastery_score": 92.0,
    "assisted_attempts_count": 1,
    "independent_attempts_count": 1,
    "evidence_notes": "Verified via unassisted conditional challenge."
  }
  ```

### `GET /assessments/tasks`
Lists all assessment tasks. Supports filtering by `role_name` and `skill_id`.

### `POST /assessments/submit`
Evaluates a code submission against deterministic rubrics.
- **Request Body:**
  ```json
  {
    "task_id": "task_python_oop_assisted",
    "submission_text": "class BankAccount: ...",
    "hints_used": 1,
    "time_taken_seconds": 45
  }
  ```
- **Response:**
  ```json
  {
    "attempt_id": 4,
    "task_id": "task_python_oop_assisted",
    "skill_id": "python_oop",
    "is_independent": false,
    "hints_used": 1,
    "score_percentage": 100.0,
    "new_skill_status": "demonstrated_assisted",
    "rubric_feedback": { "passed": true },
    "message": "Assessment evaluated. Review graduated recommendations."
  }
  ```

---

## 3. Rules, RAG & Agent Endpoints

### `GET /rules/explore`
Executes forward-chaining evaluation against the current student's facts, returning the complete audit trail of fired and non-fired rules.

### `GET /rules/verify-goal`
Executes backward chaining to prove whether a target goal competency satisfies all prerequisites.
- **Query Parameter:** `goal_skill=python_fastapi`

### `POST /chat/query`
Grounded local RAG query endpoint.
- **Request Body:**
  ```json
  {
    "message": "How do classes work in Python?",
    "hint_step": 1
  }
  ```
- **Response:**
  ```json
  {
    "reply": "...",
    "is_fallback": true,
    "model_used": "Deterministic Rule-Based Knowledge Engine (Offline)",
    "source_citations": [
      { "source": "python_oop_guide.md", "section": "Chunk 1" }
    ],
    "retrieved_passages": [ ... ]
  }
  ```

### `POST /agent/run`
Executes the 8-state bounded learning agent workflow.
- **Request Body:** `{"goal": "Optimize next learning milestone"}`
- **Response:** Full execution trace with step numbers, decisions, tool names, and final recommendations.

---

## 4. Algorithm Lab Practicals Endpoint

### `GET /algorithms/practical/{id}`
Executes any of the 16 syllabus practicals ($id \in [1, 16]$).
- **Optional Query Parameter:** `param` (e.g. `param=4` for 4 disks in Hanoi, `param=cough,runny_nose` for medical symptoms).
