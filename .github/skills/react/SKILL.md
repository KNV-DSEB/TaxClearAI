---
name: react
description: Reviews React code for hooks correctness, component patterns, performance, and (when the project uses Next.js) App Router idioms. Activates when explicitly asked to review React/Next.js code — not run automatically on every edit.
applies_to: react
---

This is an on-demand deep review — the baseline expectations this code should already meet come from `.github/instructions/*.instructions.md` (the `frontend-structure` rule). The "Next.js App Router" and "Server vs. Client Boundary" sections below only apply if this project uses Next.js — skip them for a plain React + Vite project.

**React Hooks**
- `useEffect` dependency array must include every value from component scope used inside
- Cleanup function returned from `useEffect` for subscriptions and timers
- `useCallback` wraps functions passed as props to memoized children
- `useMemo` for expensive computations; not for every derived value (trust the profiler)
- Custom hooks extract reusable stateful logic; never just wrap a single `useState`

**Component Patterns**
- Prefer composition (`children`, render props) over prop drilling or inheritance
- `React.memo` only where profiling shows a re-render cost — not preemptively
- `key` prop on list items must be stable and unique (not index unless the list is static)
- Avoid storing JSX in state; store data and derive JSX in render

**Next.js App Router (Next.js projects only)**
- Server Components by default; add `"use client"` only when you need browser APIs or interactivity
- Data fetching in Server Components with `fetch` (auto-deduplicated and cached)
- `loading.tsx` and `error.tsx` colocated with each route segment
- `generateStaticParams` for static routes; `revalidate` export for ISR
- `next/image` for all images: specify `width`/`height` or `fill` + `sizes`
- `next/font` for font loading — never `@import` in CSS

**Server vs. Client Boundary (Next.js projects only)**
- Do not import server-only modules in Client Components
- Serialize only plain objects across the server→client boundary (no class instances, functions)
- `"use server"` actions for form mutations; validate and authorize on the server side

**State & Data**
- React Query or SWR for server state; Zustand/Jotai (or similar) for client global state
- Never fetch in `useEffect` when a library handles caching and revalidation
- Optimistic updates with proper rollback on error

**Performance**
- Route-level code splitting is automatic in most setups; lazy-load heavy client components
- Avoid hydration mismatches: no `Math.random()`, `Date.now()`, or non-deterministic output in render
- `<Suspense>` boundaries around async subtrees

**Testing**
- React Testing Library: query by role/label text, not by test ID or CSS class
- `userEvent` over `fireEvent` for realistic interaction simulation
- Mock `fetch` or use `msw` (Mock Service Worker) for network mocking

Flag: missing deps in `useEffect`, `"use client"` overuse, index keys, missing `error.tsx`, hydration risks.
