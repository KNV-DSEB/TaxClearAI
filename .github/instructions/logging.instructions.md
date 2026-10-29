---
---

## 13. Logging

- Structured logs only (JSON), never a bare free-text `console.log`/`print` in a production code path — use the project's logger (Winston/Pino for Node, `logging`/`structlog` for Python).
- Every log entry gets the correct level: `debug` (dev-only diagnostics), `info` (normal operational events), `warn` (unexpected but not broken), `error` (a single operation failed), never log-and-continue silently on something that should be an `error`.
- Every log carries context: a correlation/request ID that propagates across the whole request lifecycle, plus the relevant entity ID (user ID, order ID, etc.) — a log line must be useful in isolation.
- NEVER log secrets, passwords, tokens, full card numbers, or raw PII (emails/phone numbers) — mask or omit them.
