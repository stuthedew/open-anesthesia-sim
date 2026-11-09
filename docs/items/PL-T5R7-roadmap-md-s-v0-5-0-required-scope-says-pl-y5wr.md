---
id: PL-T5R7
title: ROADMAP.md's v0.5.0 Required scope says PL-Y5WR makes the 30-day scenario cap an explicit halt, while the v0.4.7 version row says the cap became 24 h, enforced by the step count, before v0.5.0 shipped
priority: P2
effort: S
status: ready
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
payoff: The roadmap states the run limit the simulator enforces, 24 hours, instead of a 30-day cap that never shipped.
verify: ! grep -qF 'The 30-day scenario cap becomes an explicit halt' ROADMAP.md
---

**Problem.** ROADMAP.md's v0.5.0 Required scope says PL-Y5WR makes the 30-day scenario cap an explicit halt, while the v0.4.7 version row says the cap became 24 h, enforced by the step count, before v0.5.0 shipped

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 57 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: PL-Y5WR says "the 30-day scenario cap becomes an explicit halt" (5280-5282). Version row 72 (v0.4.7) says the cap became 24 h, enforced by the step count, before v0.5.0 shipped.
```

**Why it matters.** The longest run a learner can set is a limit on what the simulator does. The two passages give different limits and different ways of enforcing them.

**Done when.** v0.5.0's entry for `PL-Y5WR` says what shipped: the supported run length became 24 hours, enforced as an explicit halt, in v0.4.7, before v0.5.0.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The v0.4.7 row's account of the 24 h cap is now in `PL-H1GH`'s brief.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. The 30-day scenario cap sentence and the row giving 24 hours were both in `ROADMAP.md` at `817a4d88`.

**Checked 2026-11-09:** v0.5.0's Required scope still has "The 30-day scenario cap becomes an explicit halt (queue item PL-Y5WR)". `PL-Y5WR` closed in v0.4.7, and the limit the model enforces is the 24-hour supported run length, as the v0.7.0 frozen-list entries `PL-KHXB` and `PL-VHQX` say. The v0.4.7 row's account moved to `PL-H1GH`'s brief, so `ROADMAP.md` now states only the 30-day cap.

**Generator check.** One-off: a finding from the `ROADMAP.md` structure-read sweep. The fact misread is whether one `ROADMAP.md` passage still agrees with a later record of the same thing. No head's `misread:` states that fact for `ROADMAP.md`, and the cluster came from one deliberate read rather than from a mechanism that keeps producing it.
