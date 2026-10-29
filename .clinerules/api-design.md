## 14. API Design

- Nouns, not verbs: `/users` not `/getUsers`. Plural collections. Nested resources for relationships (`/users/{id}/orders`). kebab-case in paths, camelCase in JSON bodies.
- Version in the URL (`/api/v1/...`) — never a breaking change on an existing version.
- Respect HTTP method semantics: `GET` never mutates state; `PUT` replaces the whole resource; `PATCH` partially updates; `POST` on a collection returns `201 Created` + `Location`; `DELETE` returns `204 No Content`.
- One consistent response envelope and one consistent error format (RFC 7807 — see the Code Style rule) across every endpoint. Never remove/rename a field in an existing response; add new fields as optional.
- Pagination on every list endpoint (see the Performance rule) — never return an unbounded list.
