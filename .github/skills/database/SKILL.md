---
name: database
description: Reviews database schema, queries, and access patterns for correctness, performance, and maintainability. Activates when explicitly asked to review the schema, a migration, or slow queries — not run automatically on every edit.
applies_to: backend
---

This is an on-demand deep review, complementing `.github/instructions/*.instructions.md` (this project's backend/architecture rules, which don't go into schema/query-level detail).

**Schema Design**
- Tables in at least 3NF unless a deliberate denormalization decision is documented
- Primary keys: surrogate (`BIGINT AUTO_INCREMENT` or `UUID`) preferred over composite business keys
- Foreign keys declared with `ON DELETE` / `ON UPDATE` policies that match business rules
- `NOT NULL` constraints on columns that must always have a value
- `UNIQUE` constraints enforcing business uniqueness at the DB level (not just application)
- Consistent naming: `snake_case`, singular table names, `table_id` for PKs

**Indexing**
- Every FK column should have an index (not automatic in all DBs)
- Composite indexes ordered: highest-cardinality / most-filtered column first
- Covering indexes for frequent SELECT patterns that return few columns
- Flag: indexes on low-cardinality columns (boolean, enum with few values)
- Flag: `SELECT *` queries that defeat covering indexes

**Query Quality**
- N+1 pattern: single-row queries inside loops — replace with `IN (...)` or a JOIN
- Missing `LIMIT` on unbounded SELECT in application code
- Functions on indexed columns in `WHERE` defeat the index (`WHERE YEAR(created_at) = 2026` → `WHERE created_at BETWEEN ...`)
- Implicit type coercions in JOINs or WHERE (e.g. comparing INT to VARCHAR)
- Subqueries that could be rewritten as JOINs for a better query plan

**Transactions**
- Transactions wrap all operations that must succeed or fail together
- Long-running transactions release locks for too long — identify and shorten
- Optimistic locking (`version` column) for concurrent updates to the same row
- Deadlock risk when multiple transactions acquire locks in inconsistent order

**Migrations**
- Each migration is reversible (has a `down` script)
- Adding `NOT NULL` columns on populated tables requires a default value first
- Column renames done in two phases to support rollback (add + copy + drop)
- Index creation done concurrently (e.g. Postgres `CONCURRENTLY`) to avoid a table lock

**Connection Management**
- Connection pool sized appropriately for the app's concurrency model
- Pool not shared across async workers that use blocking drivers

Produce: schema findings, slow query candidates, and migration safety issues.
