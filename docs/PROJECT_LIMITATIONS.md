# MERIDIAN — System Limitations & Future Work

## 1. Automated Code Evaluation Boundaries
- Current code evaluation relies on deterministic keyword analysis, structure verification, and rubric patterns.
- Arbitrary untrusted code execution (such as `exec()` or compilation on the host machine) is intentionally disabled to preserve the security of student hardware and avoid remote code execution (RCE) vulnerabilities.
- *Future Work:* Introduce secure containerized sandboxes (e.g., lightweight gVisor or WebAssembly WASI runtimes) to execute unit tests against student code without host vulnerability.

## 2. Local Model Hardware Bounds
- The application uses `llama3.2:3b` as its candidate local LLM via Ollama, fitting comfortably within laptops with 16 GB RAM.
- While 3B models run fast on standard CPUs, complex mathematical proofs or multi-turn reasoning may occasionally deviate without strong system prompting.
- When Ollama is offline or resource-constrained, MERIDIAN's deterministic offline fallback engine steps in seamlessly to provide grounded textbook passages and prevent system stalls.

## 3. Academic Integrity Scope
- MERIDIAN strictly enforces no-hint policies and separate tracking for `demonstrated_assisted` versus `demonstrated_independently` states within its UI and database.
- It does not claim to prevent external assistance (e.g., student using another device or browser). Independent assessments are designed for supervised lab exam settings or proctored competition checks.
