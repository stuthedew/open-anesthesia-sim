---
id: PL-F0L8
title: Establish what accessibility Flet's rendering backend can actually deliver
status: untriaged
feature: presentation-safety
added: 2026-09-02
---

**Problem.** `ROADMAP.md:1727` (Phase 2, item 20) commits to "keyboard
navigation, contrast, screen-reader support, color-vision-safe encodings".
Contrast and colour-vision encodings are ours to control and are covered by
`PL-MMYM`, `PL-1MK1` and `PL-GVXP`. Keyboard navigation and screen-reader
support are not: they are delivered by Flet's rendering backend, and nobody has
established what that backend actually exposes. Flet renders through Flutter,
which draws to a canvas rather than emitting a native accessibility tree, and
the fidelity of the semantics layer it synthesises — and how it behaves in the
desktop versus the web target — is an open question this project has never
asked.

**Why it matters.** It bounds a roadmap commitment that is already written down.
If the backend cannot deliver usable screen-reader semantics for the readouts
and the chart, then item 20 as phrased is partly unachievable, and the honest
responses are to narrow it, to add a non-visual route to the same values (a text
summary of the chart, an exportable table), or to accept the limit and say so.
All three are cheaper to choose now than during Phase 2 with controls already
built on top. It may also bear on the far-future packaging and distribution
question (`ROADMAP.md` item 23), since desktop and web targets may not answer
the same.

This is a scoping question, not a defect. It is filed because a commitment whose
feasibility is unknown is worth converting into one whose feasibility is known,
before the phase that depends on it starts.

**Approach.** Answer three things against current Flet and Flutter
documentation and a hands-on check of the running app, not from memory:

1. What semantics the current UI exposes to a screen reader in each target, and
   whether the numeric readouts are reachable and announced with their units.
2. Whether the controls are keyboard-reachable and focus-visible in tab order,
   and what SC 2.4.7 / 2.4.11 conformance would require.
3. What the chart exposes, and whether a non-visual equivalent is the realistic
   answer rather than making the canvas itself accessible.

Record the answers, then either narrow `ROADMAP.md` item 20 to what is
achievable or file the items that close the gap.

**Where.** `ROADMAP.md:1727` (item 20); `src/anesthesia_sim/app/`.

**Done when.** `ROADMAP.md` item 20 states what is achievable on this stack
rather than what would be ideal, and the reasoning is recorded where a later
session will find it before re-asking.
