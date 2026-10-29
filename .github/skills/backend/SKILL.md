---
name: backend
description: Reviews backend code for architectural correctness and production readiness — layering, error handling, input validation, logging, configuration, resiliency, and concurrency. Activates when explicitly asked to review backend code or before a release — not run automatically on every edit.
applies_to: backend
---

This is an on-demand deep review — the baseline expectations this code should already meet come from `.github/instructions/*.instructions.md` (this project's `backend-mvc` and `architecture` rules).

**Layered Architecture**
- Controller/Router: only request parsing, validation, delegation — no business logic
- Service: business rules, orchestration — no HTTP or DB concerns
- Repository: data access only — no business logic
- Flag any cross-layer leakage

**Error Handling**
- All exceptions caught at the appropriate layer; not swallowed silently
- Domain errors mapped to meaningful HTTP responses
- Global exception handler prevents raw stack traces reaching clients
- Retry logic on transient errors (network, DB deadlock)

**Input Validation**
- Validate all external input at the boundary (controller or DTO)
- Reject invalid data early; do not pass invalid state deeper
- Validate content type and size for file uploads

**Logging & Observability**
- Structured logs (JSON format preferred) with a correlation/trace ID
- Log at the right level: DEBUG for dev detail, INFO for business events, WARN for recoverable issues, ERROR for failures
- No sensitive data (passwords, tokens, PII) in logs
- Key metrics: request count, latency, error rate, queue depth

**Configuration**
- No hardcoded URLs, ports, or credentials — use environment variables
- Secrets loaded from a vault or env, never from source-controlled files
- Fail fast on missing required configuration at startup

**Resiliency**
- Timeout on every external service call
- Graceful degradation when optional dependencies are unavailable
- Health check endpoint that reflects real readiness (DB connectivity, queue)

**Concurrency & Thread Safety**
- Shared mutable state protected appropriately
- Stateless services where possible (easier horizontal scaling)
- Async boundaries explicit and consistent

Summarize: layer violations, missing error handling paths, and top-3 production risk items.
