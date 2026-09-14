---
id: PL-C4RS
title: Gate 1's group headings and v0.5.0's Required scope disagree on three ids, and ROADMAP.md states Required scope as the test
status: untriaged
added: 2026-09-14
---

**Problem.** Gate 1's group headings and v0.5.0's Required scope disagree on three ids, and ROADMAP.md states Required scope as the test

**Found while building `PL-WZBX`** (the gate counted milestone work as
clearable before the milestone), whose first step was to check v0.5.0's
`Required scope` against the entries Gate 1 writes under "Cleared by v0.5.0
itself" before resting the implementation on that test. Seven of the eight are
in it. Three *other* ids are in it too, under headings saying the opposite:

- `PL-2FM6` and `PL-8LXM` — under "Cleared by the `v0.4.x` track, ahead of this
  gate — 7 entries".
- `PL-GVXP` — under "Cleared before v0.5.0 begins, the product lane — 39
  entries".

**Why it matters, and why it is not urgent.** `ROADMAP.md` § "Debt inside the
milestone's own scope" states one test — "whether the item appears in the
milestone's `Required scope`" — and then says an item passing it "is listed in
the frozen gate under a heading that says so". Three are not. All three have
closed, so nothing rode on it while `PL-WZBX` was built and the gate reads the
same either way today; it matters the next time a gate is frozen, because a
reader taking the headings as the record and a session taking the rule get
different answers about who clears an entry.

**Where.** `ROADMAP.md` § "v0.5.0 - the case you can branch" → "Debt gate: the
frozen list", the three group headings above; or v0.5.0's `Required scope`, if
the three were named there by mistake rather than misfiled below. Which side is
wrong is a judgment on the prose rather than a parse, which is why `PL-WZBX`
did not settle it in passing: it reads the rule, not the headings
(`subprojects/docket/src/docket/roadmap.py`, `gate_status`).

**Done when.** Each of the three either moves under a heading matching what
`Required scope` says of it, or leaves `Required scope`, with the correction
dated in the section the way that list records its other post-freeze notes.
