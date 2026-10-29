---
name: ui-design-review
description: Static audit checklist for existing UI — layout, spacing, typography, forms, animation, navigation, and anti-slop consistency rules. Not for component architecture, hooks, or accessibility (see `frontend`) or for designing new UI (see `ui-design`).
applies_to: frontend
---

# UI Design Review

Review files against these groups. Report findings as `file:line — issue`, grouped by file, terse, skip explanation unless the fix is non-obvious. Accessibility is intentionally not repeated here — see the `frontend` skill's Accessibility section for that.

> Checklist adapted from Vercel's Web Interface Guidelines, `taste-skill`, and `ui-ux-pro-max-skill` — see `NOTICE.md` next to this file for full attribution.

**Focus states**
- Interactive elements need visible focus (`focus-visible:ring-*` or equivalent); never `outline: none` without a replacement
- Use `:focus-visible` over `:focus` (avoid a focus ring on mouse click); group compound controls with `:focus-within`

**Forms**
- Inputs need `autocomplete` and a meaningful `name`; correct `type` (`email`, `tel`, `url`, `number`) and `inputmode`
- Never block paste; disable spellcheck on emails/codes/usernames
- Checkbox/radio label + control share one hit target — no dead zones between them
- Submit button stays enabled until the request starts, with a spinner during the request — never disabled pre-emptively
- Errors inline next to the field; focus the first error on submit
- Warn before navigating away with unsaved changes

**Animation**
- Honor `prefers-reduced-motion`
- Animate only `transform`/`opacity` (compositor-friendly); never `transition: all` — list properties explicitly
- Animations must be interruptible — respond to user input mid-animation, don't block on it
- Animate at most 1–2 key elements per view — animating everything that moves on screen causes distraction, not delight
- Easing has a purpose: decelerate (`ease-out`) for something arriving, accelerate for something leaving, linear only for constant-rate progress (a spinner) — one easing curve copy-pasted onto every transition is a tell

**Typography**
- `…` not `...`; curly quotes `"` `"` not straight `"`; loading states end with `…` (`"Saving…"`)
- `font-variant-numeric: tabular-nums` for number columns/comparisons
- `text-wrap: balance` (or `text-pretty`) on headings to prevent orphan words

**Content handling**
- Text containers handle long content (`truncate`, `line-clamp-*`, `break-words`); flex children need `min-w-0` to allow truncation
- Empty states handled explicitly — never render broken UI for an empty string/array
- User-generated content: design for short, average, and very long inputs, not just the demo value

**Images**
- `<img>` has explicit `width`/`height` (prevents layout shift)
- Below-fold images lazy-load; above-fold critical images get priority loading

**Performance**
- Large lists (>50 items) are virtualized, not rendered in full
- No layout reads in render (`getBoundingClientRect`, `offsetHeight`, `scrollTop`) — these force synchronous reflow
- Prefer uncontrolled inputs; a controlled input's per-keystroke work must stay cheap

**Navigation & state**
- URL reflects state — filters, tabs, pagination, expanded panels live in query params, not only component state
- Deep-linkable UI stays deep-linkable after a refresh
- Destructive actions need a confirmation modal or an undo window — never immediate and silent
- Breadcrumbs earn their place at 3+ levels of hierarchy; on a flat or shallow site they're clutter
- The current nav item/section has a visible active state (color, underline, weight) — "no visual feedback on current location" is the single most common navigation miss

**Touch & interaction**
- `touch-action: manipulation` (avoids the double-tap-zoom delay)
- `overscroll-behavior: contain` inside modals/drawers/sheets — background page shouldn't scroll through them
- `autoFocus` used sparingly — desktop only, one primary input, avoided on mobile
- Hover-only interactions have no equivalent on touch devices — any hover-revealed control needs a tap/click path too

**Dark mode & theming**
- `color-scheme: dark` set on `<html>` for dark themes (fixes native scrollbar/input rendering)
- Native `<select>` gets explicit `background-color`/`color` (breaks in some OS dark modes otherwise)

**Locale & i18n**
- Dates/times/numbers formatted via `Intl.DateTimeFormat`/`Intl.NumberFormat`, not hand-built strings

**Hover & interactive states**
- Every button/link has a `hover:` state; interactive states (hover/active/focus) read as more prominent than resting state, not less

**Content & copy**
- Active voice ("Install the CLI", not "The CLI will be installed")
- Specific button labels ("Save API Key", not "Continue"); error messages state the fix, not just the problem

**Consistency & anti-slop**
- One accent color, locked — it means the same thing everywhere on the page, no random second accent three sections down
- One corner-radius scale, locked — all-sharp, all-soft, or a documented per-component rule, applied everywhere
- No duplicate CTA intent on one page — "Get in touch" / "Contact us" / "Let's talk" are the same intent, pick one label and reuse it
- Hero fits the initial viewport — headline, subtext, and CTA visible without scrolling on desktop
- "Eyebrow" labels (small uppercase tags above a section heading) rationed to at most 1 per 3 sections
- Button text never wraps — a CTA label wrapping to 2+ lines at desktop width is broken, shorten the label or widen the button

**Anti-patterns to flag directly**
- `user-scalable=no` / `maximum-scale=1` (disables pinch-zoom)
- `outline-none` with no focus-visible replacement
- `<div>`/`<span>` with a click handler instead of `<button>`
- Images without dimensions; large `.map()`-rendered arrays without virtualization
- Hardcoded date/number formatting instead of `Intl.*`

Flag order, most severe first: broken keyboard/focus flow, missing async/destructive-action feedback, layout-shifting images, accent-color or corner-radius inconsistency, duplicate CTA intent, unexplained motion or `transition: all`, generic/passive copy.
