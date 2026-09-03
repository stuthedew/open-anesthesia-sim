---
id: PL-9K7K
title: docket next offers PL-ZRSP first, but PL-ZRSP's own brief says to land it after PL-DR1Z
status: untriaged
added: 2026-09-03
---

**Problem.** `bin/docket next` ranks `PL-ZRSP` (plot the F_A/F_I ratio) first
among the v0.4.0 items: `P1`, `S`, `ready`, in scope for the step the project
is on. Its own **Safety notes.** section says the opposite — "The control-input
timeline (`PL-DR1Z`) is what makes that visible, so land this after it" —
because F_A/F_I is the textbook wash-in curve only while inspired
concentration is held constant, and a dial change mid-run reads as uptake to a
learner who cannot see when the dial moved. The ordering is stated in prose the
ranking cannot read, so every session that asks what to do next is pointed at
the one v0.4.0 item its own brief defers.

**Why it matters.** This is the safety half of the item, not a preference: the
whole reason `PL-DR1Z` comes first is that the trace is misreadable without it.
A ranking that contradicts a brief's safety note is worse than one that is
merely unhelpful, because the session that follows it has been told twice and
will believe the tool.

**Where.** `docs/items/PL-ZRSP-plot-the-f-a-f-i-ratio-the-uptake-literature.md`
(the **Safety notes.** paragraph), and whatever front-matter states the order —
`blocked-by: PL-DR1Z` with `status: blocked` is the representable form, and is
what `PL-VM40` already uses for a sequencing-only block.

**Not done here** because `PL-ZRSP`'s file is being edited on
`origin/claude/core-refactor-open-items-q99gen` (pull request #264, the v0.4.1
queue audit) as this was found; two edits to one file is a merge conflict for
no gain. Apply it once #264 has merged, and re-read the brief first: that
branch adds a note to this item about the F_C = F_I assumption, which may
change how the ordering should be stated.

**Done when.** `bin/docket next` no longer offers `PL-ZRSP` ahead of
`PL-DR1Z`, and the ordering lives in the front matter rather than only in the
brief's prose.

**Found.** 2026-09-03, answering "what next" against the v0.4.0 queue.
