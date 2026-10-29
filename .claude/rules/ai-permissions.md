## 11. AI Agent Permissions

**Allowed without asking**: read files, grep codebase, run lint/format on a single file, run unit tests on a single file, create a new module folder following the pattern above, create a git branch/commit.

**Requires approval**: install new packages/dependencies, modify `package.json`/`pyproject.toml` scripts, modify database migration files, push to main/develop, delete files or folders, change environment variable structure, modify CI/CD workflow files.

**Never do**: commit secrets or credentials, push directly to main, skip MVC layers (controller → DB directly), remove security middleware, disable tests to make a build pass.
