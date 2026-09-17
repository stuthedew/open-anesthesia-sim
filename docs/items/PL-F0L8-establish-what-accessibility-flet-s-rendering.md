---
id: PL-F0L8
title: Establish what accessibility Flet's rendering backend can actually deliver
priority: P3
effort: M
status: dropped
classes: planning
feature: presentation-safety
touches: ROADMAP.md, src/anesthesia_sim/app
reason: Superseded by the Qt port. The investigation this item commissions is against Flet, which v0.5.1 replaces with PySide6; ROADMAP.md "Items this port moots or transforms" records that after the port the question is QAccessible's, a different investigation against a different backend. The surviving half - settling ROADMAP item 20 - is PL-QR6Q, blocked-by v0.5.1.
closed: 2026-09-13
added: 2026-09-02
---

> **The Qt port moots or transforms this.** `ROADMAP.md` § "Completed: v0.4.26 -
> the interface moves to Qt" names this item under "Items this port moots or
> transforms". Read that entry before starting: the work may be thrown away by
> the port, or may be a different question after it. Found 2026-09-10.

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

**Decision needed.** Whether `ROADMAP.md` item 20 stays as written or is
narrowed to what this stack can deliver - and, if the backend cannot expose
usable semantics, which of three answers the project takes: narrow the
commitment, add a non-visual route to the same values (a text summary of the
chart, an exportable table), or accept the limit and document it. The
investigation below is what makes that answerable; it is not itself the
decision.

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

## Dropped 2026-09-13: the investigation is against a backend the project has decided to replace

**This is not a new decision. It is the disposition of one the project owner
already took**, on 2026-09-10 when `v0.5.1` was scoped on `PL-QXSB`.
`ROADMAP.md` § "Items this port moots or transforms" names this item outright
and states the consequence: "**`PL-F0L8`** asks what accessibility Flet's
rendering backend can deliver. After the port the question is `QAccessible`'s,
which is a different investigation against a different backend."

**Why it cannot simply wait for the port.** It is a Gate 1 entry, and that gate
clears before `v0.5.0` begins — `v0.5.1` ships *after* `v0.5.0`. So there is no
sequencing available that lets this item run against the backend it would need
to run against. Deferring it would mean holding the gate open on work that can
only ever be done wrong.

**Why the two halves separate cleanly.** The item bundles an investigation with
a roadmap question, and the port kills exactly one of them:

- **The investigation** — what Flet/Flutter's synthesised semantics layer
  exposes in each target — is worthless the day the port lands. Flutter draws
  to a canvas and synthesises semantics; Qt exposes `QAccessible`, which bridges
  to the platform accessibility API. A finding about one is not evidence about
  the other.
- **The commitment** — whether `ROADMAP.md` item 20 stays as written or is
  narrowed — survives untouched. No toolkit change retires a promise about
  keyboard navigation and screen-reader support.

So the investigation is dropped and the commitment is re-pointed. **`PL-QR6Q`**
carries it, `blocked-by: v0.5.1`, with the three questions rewritten against Qt
and `pyqtgraph`.

**`dropped`, not `done`**, on the precedent this roadmap sets for `PL-NGF7`:
"Expected disposition when `v0.5.1` lands: `dropped`, not `done` — the port
resolves it rather than any work on it. That is recorded now so a later session
does not read a dropped item as one that was skipped." The same applies here,
and the same sentence is the reason this block exists: nobody did the work, and
nobody should.

**What it differs from, and why that is not a precedent problem.** `PL-NGF7` is
held open until the port proves the defect gone, because it is a defect whose
disappearance is a fact about the shipped tree. This is an open *question*, and
a question whose premise is void is answerable now.

**Gate effect.** One entry leaves Gate 1 by the route its own definition of done
allows — "`dropped` with its reason recorded" — rather than by deferral. Its
Gate 1 line stays written where the freeze put it, per § "The gate is a
snapshot, not a moving target".
