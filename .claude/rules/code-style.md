## 7. Code Style Rules

- NEVER swallow exceptions silently. ALWAYS log errors with context (request ID, user ID if available) — see the Logging rule.
- Return RFC 7807 Problem Details format for API errors (`type`, `title`, `status`, `detail`, `instance`).
- ALWAYS use async/await, never raw callbacks. ALWAYS handle Promise rejections. TypeScript: annotate async return types. Python: `async def` + `await` throughout FastAPI.
- Comment WHY, not WHAT. Public functions/methods get a one-line docstring/JSDoc only when the signature alone doesn't explain intent.
