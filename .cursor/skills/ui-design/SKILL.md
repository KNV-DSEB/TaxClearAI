---
name: ui-design
description: Aesthetic direction for building or reshaping frontend UI — deliberate visual identity, typography, and layout choices before writing code. Not for auditing UI that already exists (see `ui-design-review`) or component architecture/performance (see `frontend`).
applies_to: frontend
---

# UI Design

Approach this as the design lead at a small studio known for giving every client a visual identity that could not be mistaken for anyone else's. The client has already rejected proposals that felt templated and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout specific to this brief, and take one real aesthetic risk you can justify.

> Adapted from Anthropic's `frontend-design` skill (`github.com/anthropics/skills`, Apache License 2.0) — see `NOTICE.md` next to this file for full attribution.

**Ground it in the subject.** If the brief doesn't pin down what the product or subject is, pin it yourself first: name one concrete subject, its audience, and the page's single job. The subject's own world — its materials, vernacular, artifacts — is where distinctive choices come from, not a generic template.

**Avoid the three defaults.** AI-generated design right now clusters around three looks: (1) warm cream background (~#F4F1EA) with a high-contrast serif display and a terracotta accent, (2) near-black background with one bright acid-green or vermilion accent, (3) broadsheet layout with hairline rules, zero border-radius, dense newspaper columns. All three are legitimate for some briefs, but they're defaults, not choices — they show up regardless of subject. Where the brief pins down a direction, follow it exactly. Where it leaves an axis free, don't spend that freedom on one of these three.

**Work in two passes.** First, brainstorm a compact token system before touching code:
- **Color** — 4–6 named hex values, not "primary/secondary" abstractions
- **Type** — a characterful display face used with restraint + a complementary body face (+ a utility face for captions/data if needed)
- **Layout** — a one-sentence concept plus an ASCII wireframe
- **Signature** — the one element this page will be remembered by

Then review that plan against the brief: if any part reads like the generic default for any similar page rather than a choice made for this brief, revise it and say what changed and why. Only after confirming the plan's specificity should code follow it exactly.

**Structure, motion, and complexity are choices, not decoration.** Numbered markers (01/02/03), dividers, and eyebrows should encode something true about the content (a real sequence), not decorate an arbitrary list. Motion should serve the subject — a page-load sequence or scroll-triggered reveal beats scattered hover effects, and often less is more (excess animation reads as AI-generated). Match execution complexity to the vision: maximalist directions need elaborate execution, minimal directions need precision in spacing and detail.

**Restraint.** Spend boldness in one place — the signature element — and keep everything around it quiet. Build to a quality floor without announcing it: responsive to mobile, visible keyboard focus, reduced motion respected (these overlap with the `frontend` skill's a11y checklist — satisfy both, don't treat them as separate passes).

**Copy is design material.** Before writing any UI text, ask what it needs to say and how that helps the person using the interface, not how to describe the feature. Write from the user's side of the screen — name things by what people control and recognize ("notifications", not "webhook config"). Default to active voice: a control names exactly what happens ("Save changes", not "Submit"), and an action keeps its name through the whole flow (a "Publish" button produces a "Published" toast). Errors state what happened and how to fix it, in the interface's voice, never vague or apologetic. Empty states are an invitation to act, not a dead end.

Before calling the work done, hold it against `ui-design-review`'s checklist.
