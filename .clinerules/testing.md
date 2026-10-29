---
globs: "**/*.spec.ts,**/*.test.ts,**/test_*.py"
---

## 8. Testing Rules

- Coverage target: 80% minimum.
- Unit tests alongside source (`*.spec.ts` or `test_*.py`); integration tests in `tests/integration/`; e2e in `tests/e2e/`.
- Mock external services — NEVER call real APIs in unit tests.
- Test naming describes behavior, not "should": ✓ `"returns 401 when token is expired"`, ✗ `"should return 401 when token is expired"`.
