---
---

## 2. Architecture Rules — MVC + Module Pattern

### MVC + Module pattern (NON-NEGOTIABLE)

```
Request → Controller/Router → Service → Repository → Model/Entity
```

- **Controller/Router**: ONLY receive request, validate input shape, call service, return response. NEVER contain business logic, NEVER query DB, NEVER import ORM/DB session directly.
- **Service**: ALL business logic lives here. MAY call multiple repositories and orchestrate operations. NEVER import ORM models to query DB directly. NEVER duplicate logic that exists in another service — compose instead.
- **Repository**: The ONLY layer allowed to query the DB. Returns domain objects, not raw DB rows. NEVER contains business logic or validation. Lives inside its feature's own `modules/[feature]/` folder, next to the controller/service — NOT in a shared top-level `repositories/` folder.
- **Model/Entity**: Data definition ONLY (ORM decorators/columns). NEVER contains business logic methods. Stays a separate top-level folder (`entities/` or `models/`).

This chain applies to every framework this project uses. Concrete file-naming and violation examples for your specific backend framework are in `backend-mvc.md` and, if this project has a frontend, in `frontend-structure.md`.

### Module structure rule

Each business domain = one module folder. New feature = new module folder. NEVER add unrelated functionality into an existing module. Do not add or remove top-level folders (`modules/`, `core/`, the model/entity folder, etc.) — the folder shape is a hard contract, not a suggestion.
