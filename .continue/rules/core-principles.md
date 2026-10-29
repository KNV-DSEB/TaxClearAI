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

## 3. Naming Conventions

**TypeScript**
- Files: `kebab-case.type.ts` (e.g. `create-user.dto.ts`, `auth.service.ts`)
- Classes: `PascalCase`
- Variables/functions: `camelCase` with auxiliary verbs (`isLoading`, `hasError`, `getUser`)
- Constants: `UPPER_SNAKE_CASE`
- Interfaces: `PascalCase`, no `I` prefix

**Python**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Pydantic models: `PascalCase` (e.g. `LoginRequest`, `TokenResponse`)

## 4. Backend Structure — FastAPI

### Tech stack (Backend)
- **Framework**: FastAPI 0.115+ · **Language**: Python 3.12+
- **ORM/DB**: SQLAlchemy (async) + PostgreSQL, Alembic for migrations
- **Validation**: Pydantic v2 models for every request/response body
- **Auth**: `python-jose` (JWT) + `passlib[bcrypt]`
- **Package manager**: poetry (or pip + `requirements.txt` for `tool-script`)

### Module structure

```
modules/[feature]/
  ├── __init__.py
  ├── router.py         ← APIRouter — Controller in MVC, e.g. @router.post("/login")
  ├── service.py         ← [Feature]Service class — business logic
  ├── repository.py      ← ONLY layer allowed to run session.execute()
  ├── schemas.py         ← Pydantic request/response models (DTOs)
  └── dependencies.py    ← Depends() functions: get_current_user, require_admin
```

The repository lives inside its feature's module, not in a shared top-level `repositories/` folder. `models/` (the SQLAlchemy ORM classes) stays a separate top-level folder.

Cross-cutting concerns live in `core/`: `config.py` (pydantic-settings), `database.py` (async engine/session), `security.py` (JWT + hashing), `exceptions.py`, `middleware.py`, `logging.py`.

### Violation examples (AI will refuse to generate these)

```python
# ✗ WRONG – router.py querying the DB and doing business logic directly
@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.email == data.email))
    if user.is_active and user.role == "admin":
        hashed = bcrypt.hash(data.password)

# ✓ CORRECT – router.py only delegates
@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.login(data, db)
    return TokenResponse(**result)
```

- `router.py` NEVER calls `db.execute()`/`session.execute()` directly — that belongs in `repository.py`.
- `router.py` NEVER contains conditionals expressing business rules.
- `schemas.py` classes NEVER have methods containing business logic — Pydantic shape definitions only.

### Setup commands

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn src.main:app --reload
```

## 5. Frontend Structure

### Tech stack (Frontend)
- **Framework**: nextjs — Next.js 15 App Router | React 18 + Vite | Vue 3 + Vite
- **Styling**: Tailwind CSS · **State**: Zustand (React/Next) or Pinia (Vue)
- **Package manager**: pnpm

### Naming conventions

- Components: `PascalCase/PascalCase.tsx` (or `.vue`)
- Hooks: `use[Name].ts` (React/Next) · Composables: `use[Name].ts` (Vue)
- Services: `[name].service.ts` · Store files: `[name].store.ts` (`[name].store.ts` → Pinia store for Vue)

### Structure rule

```
src/
  ├── components/
  │   ├── common/       ← reusable UI (Button, Input, Modal — no business logic)
  │   └── features/     ← feature-specific components
  ├── hooks/ (or composables/ for Vue)
  ├── services/         ← ALL API calls go here, nowhere else
  ├── store/
  ├── types/
  └── utils/
```

- Every network call goes through a `services/*.service.ts` file. Components/pages NEVER call `fetch`/`axios` directly.
- `services/api.client.ts` is the ONE place that reads the API base URL from environment variables.

### Additional rules when this project is `app-fe-only`

`app-fe-only` means the backend already exists in a separate, reusable project — this project owns no data layer.

- NEVER create `backend/`, `models/`, or `repositories/` folders — there is no local backend to scaffold.
- `types/api.types.ts` must match the external API's real contract. If the contract changes, update the types first — never guess a field's shape.
- The external API base URL lives ONLY in `.env` (`NEXT_PUBLIC_API_URL` for Next.js, `VITE_API_URL` for Vite-based FE) and is read exclusively by `services/api.client.ts`.

### Violation examples

```typescript
// ✗ WRONG – component calling fetch directly
function UserProfile() {
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me`).then(...);
  }, []);
}

// ✓ CORRECT – component calls a service
function UserProfile() {
  useEffect(() => {
    usersService.getMe().then(...);
  }, []);
}
```

### Visual/UX work

Building or reshaping any UI (a new page, a redesigned section, a new component with visual weight) is not just structural — consult the `ui-design` skill for aesthetic direction before writing markup, and hold the result against `ui-design-review`'s checklist before calling it done. Both apply on top of the structure rules above, not instead of them.

### Setup commands

```bash
cd frontend
cp .env.example .env.local
pnpm install
pnpm dev
```

## 14. API Design

- Nouns, not verbs: `/users` not `/getUsers`. Plural collections. Nested resources for relationships (`/users/{id}/orders`). kebab-case in paths, camelCase in JSON bodies.
- Version in the URL (`/api/v1/...`) — never a breaking change on an existing version.
- Respect HTTP method semantics: `GET` never mutates state; `PUT` replaces the whole resource; `PATCH` partially updates; `POST` on a collection returns `201 Created` + `Location`; `DELETE` returns `204 No Content`.
- One consistent response envelope and one consistent error format (RFC 7807 — see the Code Style rule) across every endpoint. Never remove/rename a field in an existing response; add new fields as optional.
- Pagination on every list endpoint (see the Performance rule) — never return an unbounded list.

