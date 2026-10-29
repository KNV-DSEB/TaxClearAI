## 9. Git Workflow

**Branch naming**: `feature/[ticket]-description` · `fix/[ticket]-description` · `hotfix/description` · `chore/description`

**Commits** (Conventional Commits): `type(scope): description` — types: `feat|fix|docs|style|refactor|test|chore|perf|ci`

Before suggesting a PR is ready, run through the full checklist in the Code Review rule.

## 11. AI Agent Permissions

**Allowed without asking**: read files, grep codebase, run lint/format on a single file, run unit tests on a single file, create a new module folder following the pattern above, create a git branch/commit.

**Requires approval**: install new packages/dependencies, modify `package.json`/`pyproject.toml` scripts, modify database migration files, push to main/develop, delete files or folders, change environment variable structure, modify CI/CD workflow files.

**Never do**: commit secrets or credentials, push directly to main, skip MVC layers (controller → DB directly), remove security middleware, disable tests to make a build pass.

## 17. Workflow Contract

Applies to every code change, regardless of which AI tool is making it:

1. **Explain the design before writing code** for a non-trivial step — state the approach and why, before generating the diff.
2. **Verify before calling a step done** — run build/type-check/lint/test for the exact workspace you touched (e.g. `backend` vs `frontend`) after every edit. Never report a step complete without having actually run the check.
3. **Remove dead code created by the same change** — orphaned imports, now-unused functions/files — in the same change, not a follow-up.
4. **Transient failures** (network timeout, flaky test, a temporary lock file): retry exactly once. If it still fails, stop and report what was tried instead of silently skipping the check or bypassing it (no `--no-verify`, no `--force`).
5. **Report honestly** — list exactly which files changed, which commands were run, and their real output (including failures and what wasn't verified yet). Never say "done" when the build/tests haven't actually been run or are currently failing.

