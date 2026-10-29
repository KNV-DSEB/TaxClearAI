---
name: security-audit
description: Performs a deep, OWASP Top 10–mapped security audit of this project's code and dependencies. Activates when explicitly asked to check/review/audit security, find vulnerabilities, or before a release — not run automatically on every edit. Every finding is reported with CWE ID, severity, exact location, attack scenario, and remediation.
applies_to: always
---

This is an on-demand deep audit, not a substitute for `.windsurfrules` (the `security` rule this project already follows on every change) — run this when asked to specifically check/review/audit security, or before a release.

For each finding, report:
- **CWE ID** and OWASP category
- **Severity**: Critical / High / Medium / Low
- **Location**: `file:line`
- **Evidence**: the vulnerable code snippet
- **Attack scenario**: one-sentence description of how an attacker exploits this
- **Remediation**: corrected code

Cover these categories:

**A01 – Broken Access Control**
- Missing authorization on endpoints or service methods
- Insecure Direct Object References (IDOR)
- Privilege escalation paths (user → admin)
- CORS misconfiguration

**A02 – Cryptographic Failures**
- Sensitive data transmitted over HTTP
- Weak or deprecated algorithms (MD5, SHA1, DES, ECB)
- Hardcoded secrets, keys, or passwords
- Predictable tokens or insufficient entropy

**A03 – Injection**
- SQL injection (string concatenation instead of parameterized queries / ORM query builder)
- OS command injection (`subprocess` with `shell=True`, `child_process.exec` with unsanitized input)
- Template injection (server-side rendering with untrusted input)
- XML/JSON injection

**A04 – Insecure Design**
- Missing rate limiting on sensitive endpoints
- Absence of input validation at trust boundaries (controller/router layer)
- Business logic flaws (e.g., negative quantities, skipping payment steps)

**A05 – Security Misconfiguration**
- Verbose error messages leaking stack traces or DB schema
- Debug endpoints/flags enabled in production paths
- Default credentials or overly permissive roles
- Missing security headers (CSP, HSTS, X-Frame-Options)

**A06 – Vulnerable Components**

Run the dependency audit for every manifest found in the repo before reporting A06 findings:

```bash
# JS/TS workspaces (backend/, frontend/, or root) — pick whichever package manager the project uses
pnpm audit --json   # or: npm audit --json

# Python workspaces (backend/, or root for tool-script) — pick whichever is installed
pip-audit -r requirements.txt   # or: uv pip audit / safety check
```

Parse results and report each unique vulnerability with:
- Package name and affected version range
- CVE / GHSA advisory URL
- Severity (Critical / High / Moderate / Low)
- Whether it is a direct or transitive dependency
- Fix command (`npm audit fix` / `pnpm audit fix` / manual pin, or the Python-equivalent upgrade)

Pay special attention to:
- **Critical/High in production dependencies** (not `devDependencies`/dev-only extras) — these can be exploited at runtime
- Packages that parse/deserialize user input (protobuf, qs, yaml, xml, xlsx, pickle) — high-value injection targets
- Auth/crypto libraries (jsonwebtoken, passport, python-jose, passlib) — auth bypass or information disclosure risk
- Note when a vulnerability is only exploitable in dev-server mode (e.g. a bundler path-traversal CVE only matters if the dev server is exposed beyond `localhost`)

**A07 – Auth & Session Failures**
- Missing token expiration or refresh invalidation
- JWT `alg:none` or weak secret vulnerability
- Session fixation or missing CSRF protection
- Passwords stored without proper hashing (bcrypt/argon2)

**A09 – Logging Failures**
- Sensitive data (tokens, passwords, PII) written to logs
- Insufficient audit trail for security-relevant events

Conclude with a risk summary table: category → severity → file count.
