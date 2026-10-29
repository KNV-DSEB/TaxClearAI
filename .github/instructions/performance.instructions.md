---
---

## 10. Performance Rules

- API response target: p95 < 200ms.
- No N+1 queries — use eager loading / dataloader.
- Pagination required on all list endpoints (default 20, max 100).
- Cache expensive operations with an explicit TTL.
- Lazy-load heavy frontend components.
