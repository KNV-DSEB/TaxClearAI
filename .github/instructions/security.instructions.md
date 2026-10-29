---
---

## 6. Security Rules

- **Secrets**: NEVER hardcode secrets, API keys, tokens, or passwords. ALWAYS use environment variables. `.env` is gitignored; `.env.example` lists required vars WITHOUT values.
- **Input validation**: ALWAYS validate ALL user input at the Controller/Router level (class-validator DTOs, Zod, or Pydantic models depending on stack). Sanitize strings to prevent XSS. Validate file uploads: extension whitelist + size limit.
- **Auth**: JWT short-lived access token (15min) + refresh token (7d). ALWAYS check authentication before business logic. Use RBAC via middleware/guards. NEVER trust client-sent user IDs — always use token claims.
- **Database**: ALWAYS use parameterized queries / ORM, NEVER raw string interpolation. Connection pool with sensible limits. DB user has minimum required permissions.
- **API**: Rate limiting on all public endpoints. CORS configured explicitly — no wildcard in production. HTTPS enforced in production. Security headers on by default.
