---
name: codeagent
description: Executes a specific, already-planned code/test change. Required for every edit/test under this project's Workflow Contract — the main thread does intake, context-gathering, planning, and verification only; every actual file edit and every build/test run goes through this skill.
applies_to: app-only
---

Required inputs before starting (if missing, stop and ask instead of guessing):
- The specific file(s) to create/change, the expected content or diff, and why (grounded in the plan / `.cursor/rules/*.mdc` already agreed on).

Mandatory process:

1. **Edit the file**: use Edit (preferred, sends only the diff) or Write (only for a new file or a full rewrite). Never use a shell command to change file content when Edit/Write can do it.
2. **Verify immediately after editing**: run the build/type-check/test command for the exact workspace just touched. A step is not done until this has actually run.

   Commands for this project:
- Backend: `cd backend && ruff check . && mypy src && pytest`
- Frontend: `cd frontend && pnpm run build && pnpm run lint && pnpm test`

3. **Transient failures** (network timeout, flaky test, a temporary lock file): retry exactly once. If it still fails, stop, write down what fallback was tried, and report it to the caller instead of silently skipping it or using `--no-verify`/`--force`.
4. **Report honestly**: list exactly which files changed, which commands ran, and their real result (including failures), and call out anything not yet verified. Never report "done" when the build/tests haven't run or are currently failing.

This skill does not decide architecture or scope — that belongs to the planning step before it. It only executes what has already been decided, following `.cursor/rules/*.mdc` (especially the rules for clean code, backend MVC, frontend structure, and this workflow contract).
