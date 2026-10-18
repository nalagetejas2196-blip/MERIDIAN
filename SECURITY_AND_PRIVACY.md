# MERIDIAN Security, Privacy & Safety Architecture

## 1. Zero-Cost, Local-First Privacy Guarantee
- **No Cloud Data Transmission:** Student profiles, assessment submissions, code snippets, and evidence records remain strictly inside the local SQLite database (`meridian.db`).
- **No Third-Party AI API Calls:** All inference is executed locally through Ollama or our deterministic knowledge engine. Student queries are never sent to external LLM providers.

## 2. Authentication & Credential Storage
- **Password Security:** Passwords are never stored in plaintext. MERIDIAN utilizes standard Bcrypt password hashing (`passlib.context.CryptContext(schemes=["bcrypt"])`).
- **Session Tokens:** Stateless JSON Web Tokens (JWT) signed using HMAC-SHA256 with expiration timestamps.
- **Header Transport:** Transmitted via standard `Authorization: Bearer <token>` headers.

## 3. Code Execution Safety & Sandboxing Boundaries
- **No Unsafe Execution (`exec` / `eval`):** MERIDIAN deliberately does not execute arbitrary student-submitted code directly on the host machine.
- **Deterministic Rubric Verification:** Submissions are parsed and scored using structural keyword pattern checks and AST-like signature matching.
- **Host Security:** Protects student laptops against unintentional infinite loops, memory exhaustion, or accidental filesystem modifications.

## 4. Input Sanitization & Network Hardening
- **Path Traversal Protection:** File loaders restrict file reading exclusively to the designated `data/knowledge_base/` root.
- **Pydantic Validation:** All incoming API request bodies are validated against strict type annotations with automatic rejection of malformed payloads (HTTP 422).
- **CORS Configuration:** Development CORS policy is restricted to known local frontend ports (`http://localhost:5173`, `http://127.0.0.1:5173`, etc.).
