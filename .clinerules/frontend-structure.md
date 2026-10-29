---
globs: "frontend/**/*.{ts,tsx,vue}"
---

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
