---
name: code-review
description: Performs a thorough code review of a diff or file, categorizing every finding by severity (Critical/Major/Minor) with location, impact, and a concrete fix. Activates when explicitly asked to review code, review a PR/diff, or before merging a non-trivial change.
applies_to: always
---

This is an on-demand deep review — the baseline expectations this code should already meet come from `AGENTS.md` (the `code-review` rule this project follows on every change).

Categorize every finding by severity:

🔴 **CRITICAL** — Security holes, data corruption, crashes, broken business logic
🟡 **MAJOR** — Performance bottlenecks, missing error handling, maintainability debt
🟢 **MINOR** — Style, naming, missing docs, low-risk refactor opportunities

For each finding output:
- **Location**: `file:line`
- **Problem**: what is wrong
- **Impact**: why it matters
- **Fix**: concrete corrected code snippet

Checklist to cover systematically:

**Correctness**
- Null/undefined/empty-collection guards
- Off-by-one errors and boundary conditions
- Race conditions and shared mutable state
- Incorrect boolean logic or operator precedence

**Security**
- Injection (SQL, shell, template, LDAP)
- Broken authentication or missing authorization checks
- Sensitive data in logs, error responses, or URLs
- Insecure deserialization or unsafe reflection

**Performance**
- N+1 query patterns
- Unnecessary object allocation in hot paths
- Blocking I/O on async threads
- Missing caching for expensive, stable computations

**Maintainability**
- Functions exceeding 30 lines or doing more than one thing
- Deep nesting (>3 levels) that obscures control flow
- Magic numbers or strings that should be named constants
- Duplicated logic across files

**Framework idioms**
- Whether the code uses the framework correctly (NestJS, Express, FastAPI, React, Vue, ...)
- Anti-patterns specific to the detected stack

Close with:
1. Overall verdict: **Approve** / **Request Changes** / **Needs Discussion**
2. Top-3 priority fixes ordered by risk
