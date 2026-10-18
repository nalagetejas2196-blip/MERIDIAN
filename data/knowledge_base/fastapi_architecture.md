# Modern Web Development: REST APIs and FastAPI Architecture

## RESTful API Principles
Representational State Transfer (REST) is an architectural style for distributed hypermedia systems.
Key constraints include statelessness, client-server separation, uniform resource identifiers (URIs), and standard HTTP methods:
- GET: Retrieve resource representation without side effects.
- POST: Create a new resource subordinate to the specified URI.
- PUT / PATCH: Update existing resource state idempotently or partially.
- DELETE: Remove the designated resource.

## FastAPI Request Lifecycle and Pydantic Validation
FastAPI processes incoming HTTP requests using Starlette's ASGI foundation. Request bodies are automatically parsed, validated, and serialized through Pydantic schemas. If a client transmits ill-formed payload parameters, FastAPI automatically returns standardized HTTP 422 Unprocessable Entity status codes with detailed field-level validation errors.

## Database Session Lifecycle and Dependency Injection
FastAPI provides a declarative dependency injection mechanism (`Depends`). This enables database sessions (`SessionLocal`) to be opened per request and reliably closed within `finally` blocks, preventing resource connection leaks across concurrent asynchronous requests.
