---
name: frontend
description: Reviews frontend code for component architecture, accessibility (WCAG 2.1 AA), performance, data fetching, and client-side security. Activates when explicitly asked to review frontend code — not run automatically on every edit.
applies_to: frontend
---

This is an on-demand deep review — the baseline expectations this code should already meet come from `.cursor/rules/*.mdc` (the `frontend-structure` rule). Examples below use React idioms (the majority of VibeCraft's frontend options); for a Vue project, read `useMemo`/`useEffect`/hooks as their Vue `computed`/`watch`/composable equivalents — the underlying principle (derive don't duplicate, clean up subscriptions, avoid stale closures) still applies.

**Component Design**
- Single responsibility: each component renders one thing and owns one concern
- Props drilling beyond 2–3 levels → extract context or lift to a state manager
- Avoid business logic in render functions — extract to hooks/composables or utilities
- Presentational vs. container component separation maintained

**State Management**
- Local state for UI-only state; a global store for shared/server state
- Derived values computed, not stored (memoize over duplicating state)
- No stale closures in event handlers or effects (check dependency arrays)
- Avoid storing server data in both a cache and local state

**Accessibility (WCAG 2.1 AA)**
- Interactive elements are keyboard-reachable and have visible focus styles
- Images have meaningful `alt` text; decorative images use `alt=""`
- Form inputs associated with a `<label>` via `for`/`id` or `aria-labelledby`
- Color contrast ≥ 4.5:1 for normal text, ≥ 3:1 for large text
- No click handlers on non-interactive elements (`div`, `span`) without `role` and `tabIndex`
- Dynamic content updates announced via `aria-live` or focus management

**Performance**
- No inline object/array/function literals in props that create a new reference every render
- Expensive computations memoized; stable callbacks where the framework needs referential equality
- Images use responsive sizing (`srcset` or the framework's `<Image>` component)
- Code-split at route boundaries; heavy components lazy-loaded

**Network & Data Fetching**
- Loading, error, and empty states always handled
- Prefer a data-fetching library (React Query/SWR, or the framework equivalent) over manual `fetch` in an effect
- Requests deduplicated and cached; no redundant fetches on mount

**Security**
- No `dangerouslySetInnerHTML`/`v-html` with user-supplied content
- External URLs opened with `rel="noopener noreferrer"`
- API keys never in client-side source code

Flag: missing loading/error states, stale dependency arrays, inaccessible interactions, raw fetch in effects.
