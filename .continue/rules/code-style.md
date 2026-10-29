## 7. Code Style Rules

- NEVER swallow exceptions silently. ALWAYS log errors with context (request ID, user ID if available) — see the Logging rule.
- Return RFC 7807 Problem Details format for API errors (`type`, `title`, `status`, `detail`, `instance`).
- ALWAYS use async/await, never raw callbacks. ALWAYS handle Promise rejections. TypeScript: annotate async return types. Python: `async def` + `await` throughout FastAPI.
- Comment WHY, not WHAT. Public functions/methods get a one-line docstring/JSDoc only when the signature alone doesn't explain intent.

## 12. Clean Code & Simplicity

- Small, single-purpose functions; indent depth max 3 levels; name things clearly rather than cleverly.
- No dead code: no unused exports, no commented-out code, delete orphaned imports/files in the same change that made them orphaned.
- No copy-pasted logic — duplicated in ≥2 places → extract a shared function.
- No new dependency when a library already in the stack (the ORM, the validation library, the HTTP client already chosen) can do the job.
- No speculative abstraction (YAGNI) — only extract a shared layer once there are ≥2 real call sites, not "for later".

## 10. Performance Rules

- API response target: p95 < 200ms.
- No N+1 queries — use eager loading / dataloader.
- Pagination required on all list endpoints (default 20, max 100).
- Cache expensive operations with an explicit TTL.
- Lazy-load heavy frontend components.

## 13. Logging

- Structured logs only (JSON), never a bare free-text `console.log`/`print` in a production code path — use the project's logger (Winston/Pino for Node, `logging`/`structlog` for Python).
- Every log entry gets the correct level: `debug` (dev-only diagnostics), `info` (normal operational events), `warn` (unexpected but not broken), `error` (a single operation failed), never log-and-continue silently on something that should be an `error`.
- Every log carries context: a correlation/request ID that propagates across the whole request lifecycle, plus the relevant entity ID (user ID, order ID, etc.) — a log line must be useful in isolation.
- NEVER log secrets, passwords, tokens, full card numbers, or raw PII (emails/phone numbers) — mask or omit them.

## 16. Language Convention

- **Code identifiers** (variables, functions, types, DB table/column names): always English — see the Naming Conventions rule, no exceptions regardless of the project's target market.
- **Comments**: Vietnamese. Only write one when intent isn't obvious from the code (a constraint, a business reason, a workaround for a specific bug) — never restate what the line already says.
- **User-facing strings** (error messages shown to the end user, UI labels): Vietnamese. Keep them short and free of internal/technical detail (no stack traces, no raw SQL, no internal error codes) — see the Security rule on not leaking implementation details.

