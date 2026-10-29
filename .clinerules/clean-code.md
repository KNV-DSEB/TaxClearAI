## 12. Clean Code & Simplicity

- Small, single-purpose functions; indent depth max 3 levels; name things clearly rather than cleverly.
- No dead code: no unused exports, no commented-out code, delete orphaned imports/files in the same change that made them orphaned.
- No copy-pasted logic — duplicated in ≥2 places → extract a shared function.
- No new dependency when a library already in the stack (the ORM, the validation library, the HTTP client already chosen) can do the job.
- No speculative abstraction (YAGNI) — only extract a shared layer once there are ≥2 real call sites, not "for later".
