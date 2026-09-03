---
id: PL-9K7K
title: docket next offers PL-ZRSP first, but PL-ZRSP's own brief says to land it after PL-DR1Z
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items/PL-ZRSP-plot-the-f-a-f-i-ratio-the-uptake-literature.md
added: 2026-09-03
closed: 2026-09-03
pr: 269
verify: bin/docket check && grep -q 'blocked-by: PL-DR1Z' docs/items/PL-ZRSP-plot-the-f-a-f-i-ratio-the-uptake-literature.md
---

**Problem.** `bin/docket next` ranked `PL-ZRSP` (plot the F_A/F_I ratio) first
among the v0.4.0 items: `P1`, `S`, `ready`, in scope for the step the project is
on. Its own **Safety notes.** section said the opposite — "The control-input
timeline (`PL-DR1Z`) is what makes that visible, so land this after it" —
because F_A/F_I is the textbook wash-in curve only while inspired concentration
is held constant, and a dial change mid-run reads as uptake to a learner who
cannot see when the dial moved. The ordering sat in prose the ranking cannot
read, so every session that asked what to do next was pointed at the one v0.4.0
item its own brief defers.

**Why it matters.** This is the safety half of that item, not a preference: the
whole reason `PL-DR1Z` comes first is that the trace is misreadable without it.
A ranking that contradicts a brief's safety note is worse than one that is
merely unhelpful, because the session that follows it has been told twice and
will believe the tool.

**Where.** `docs/items/PL-ZRSP-plot-the-f-a-f-i-ratio-the-uptake-literature.md`
— the front matter, which is the only part of an item the ranking reads.

**Done when.** `bin/docket next` no longer offers `PL-ZRSP` ahead of `PL-DR1Z`,
and the ordering lives in the front matter rather than only in the brief's
prose.

**Worked.** `PL-ZRSP` is `status: blocked` with `blocked-by: PL-DR1Z`, and
carries a paragraph saying the block is sequencing only and why — the same shape
`PL-VM40` used for its own sequencing block. Nothing in the brief changed
meaning; the front matter now states what the prose already said. The block is
one line to reverse if the owner would rather ship the trace early with the
constant-F_I caveat carried by the label alone.

Deliberately not generalized into a check. Whether a brief's prose implies an
ordering is exactly the judgment `CLAUDE.md` says not to script, and a tool that
guessed at it would be authoritative and wrong.

**Found.** 2026-09-03, answering "what next" against the v0.4.0 queue. Captured
first rather than fixed, because `PL-ZRSP`'s file was being edited on
`origin/claude/core-refactor-open-items-q99gen` (#264) at the time; applied once
that and #268 had merged.
