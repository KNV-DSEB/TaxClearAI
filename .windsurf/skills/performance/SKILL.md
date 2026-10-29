---
name: performance
description: Performs a performance analysis identifying bottlenecks and optimization opportunities across database, memory, CPU, I/O, network, and concurrency. Activates when explicitly asked to check/review/analyze performance, before a release, or when investigating slowness — not run automatically on every edit.
applies_to: always
---

This is an on-demand deep analysis — the baseline expectations this code should already meet come from `.windsurfrules` (the `performance` rule).

For each finding report:
- **Category**: Database / Memory / CPU / I/O / Network / Concurrency
- **Severity**: High (user-visible latency) / Medium (scales poorly) / Low (micro-opt)
- **Location**: `file:line`
- **Finding**: the inefficient pattern
- **Fix**: optimized alternative with rationale

Check these areas:

**Database & Persistence**
- N+1 query patterns (loop calling single-row fetches)
- Missing indexes on filter/join/order columns
- `SELECT *` fetching unused columns
- Transactions spanning long operations or outbound HTTP calls
- Missing pagination on unbounded result sets

**Memory**
- Collecting all rows into memory before processing (stream instead)
- Large object graphs held in session or cache longer than needed
- String concatenation in tight loops (use a builder/join instead)
- Unnecessary cloning of large objects

**CPU & Algorithms**
- O(n²) or worse where O(n log n) or O(n) is achievable
- Repeated computation of the same value (memoize or hoist)
- JSON serialization/deserialization inside hot loops
- Regex compilation inside loops (compile once, reuse)

**I/O & Network**
- Sequential blocking I/O that could be parallel or async
- Missing connection pooling for database or HTTP clients
- Chatty APIs (many small requests where one batch call would work)
- Missing HTTP response caching headers on idempotent endpoints

**Concurrency**
- Locks/critical sections held longer than necessary
- Thread-per-request model under high concurrency where async/reactive would scale better
- Missing backpressure mechanisms in streaming/reactive pipelines

**Caching**
- Expensive computations with stable outputs that are never cached
- Cache missing TTL or eviction policy (unbounded growth)
- Cache used for mutable data without invalidation

End with a prioritized list: top-5 improvements ranked by expected impact.
