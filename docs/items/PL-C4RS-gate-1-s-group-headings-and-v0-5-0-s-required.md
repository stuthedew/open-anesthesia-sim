---
id: PL-C4RS
title: Gate 1's group headings and v0.5.0's Required scope disagree on three ids, and ROADMAP.md states Required scope as the test
priority: P3
effort: S
status: ready
classes: docs, defect
feature: planning-cadence
touches: ROADMAP.md, tools/doc_check.py
added: 2026-09-14
verify: python3 tools/doc_check.py check && ! grep -q 'Nineteen items, in the order the dependencies allow' ROADMAP.md
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

**Why it matters.** `ROADMAP.md` states `Required scope` as the test for what a
milestone contains, so a group heading that counts differently is a second
answer to a question the document says has one. `bin/docket wave` reads the two
structures and reports whichever it reads, which is how a disagreement becomes a
wrong number in every session's digest rather than an inconsistency in a
document nobody opens.

**The disagreement has to be re-measured before it is fixed.** The roadmap moved
on 2026-09-14 - Gate 1 cleared, `v0.4.25` was inserted ahead of v0.5.0, and
`PL-RKWB` renumbered the port - so the three ids this item named at capture are
not necessarily the three that disagree today. What is measurable now:
`ROADMAP.md`'s `### Required scope` opens "Nineteen items, in the order the
dependencies allow" while `bin/docket wave` reports `Scope ... (25 ids), 17
closed, 8 open`. `PL-4PC5` is the same gap seen from the tool's side - that
`wave` counts ids cited in the section's prose as scope entries - and it is in
flight on `origin/claude/bold-mayer-ij89qm` as of 2026-09-14, so the two answers
have to agree with each other. Whichever lands second reads the other first.

**Done when.** The `Required scope` section's stated count, the group headings
under `### Debt gate: the frozen list`, and what `bin/docket wave` reports all
name the same set, with the ids that differ listed and each one's placement
stated rather than implied.
