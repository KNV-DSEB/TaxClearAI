// Types here MUST match your actual backend's real response shape — see
// AGENTS.md "Frontend specifics": never guess a field, update this file
// first when the API contract changes.
//
// Left loose here because the exact shape depends on which backend
// framework this project's `backend/` uses (NestJS returns the object
// directly, Express wraps it in `{ data: ... }`, FastAPI uses snake_case) —
// narrow this once you know your project's actual shape.
export type HealthResponse = Record<string, unknown>;
