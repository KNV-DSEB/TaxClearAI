---
---

## 15. Code Review Checklist

Before suggesting a PR is ready, or when asked to review a diff, check:

1. **Layer boundaries** (see the Architecture rule) — Controller/Router only parses input and delegates; Service never queries the DB/ORM directly; Repository has no business logic; Model/Entity has no methods with logic. Frontend: every API call goes through `services/*.service.ts`, never inline `fetch`/`axios` in a component.
2. **Folder placement** — genuinely new feature → new `modules/<feature>/` (or `components/<feature>/`) folder; anything added to an unrelated existing module gets flagged. No new top-level folders outside the Architecture rule's contract.
3. **Security** (see the Security rule) — no hardcoded secret; every user input validated at the Controller/Router level; no raw string interpolation into a query; nothing trusts a client-sent user ID over the token's claims.
4. **Error handling & async** (see the Code Style rule) — no swallowed exception, no unhandled Promise rejection, no callback-style async mixed into an async/await codebase.
5. **Tests** — new business logic has a corresponding unit test; unit tests mock external services instead of calling them for real.
6. **Lint/type-check/tests pass**, no debug logs or commented-out code in the diff, `.env.example` updated if new env vars were added, a migration file was added if the DB schema changed.

Do not flag stylistic preferences that ESLint/Prettier/ruff/black would already catch — this checklist is for the architectural judgment calls automated formatting and linting cannot make.
