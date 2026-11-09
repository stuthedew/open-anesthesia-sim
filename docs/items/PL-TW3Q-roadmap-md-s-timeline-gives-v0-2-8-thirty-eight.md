---
id: PL-TW3Q
title: ROADMAP.md's timeline gives v0.2.8 thirty-eight entries at Size 2 M, 35 S, which adds to 37, while its frozen list holds 2 M and 36 S
priority: P2
effort: S
status: ready
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
payoff: v0.2.8's timeline row adds up, so its count can be trusted beside the others.
verify: ! grep -qF '| 2 M, 35 S |' ROADMAP.md
recurrences: 2026-11-07 PL-33FM withdrawn 2026-11-07 PL-33FM
---

**Problem.** ROADMAP.md's timeline gives v0.2.8 thirty-eight entries at Size 2 M, 35 S, which adds to 37, while its frozen list holds 2 M and 36 S

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 55 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: timeline row 1 (441) gives v0.2.8 "thirty-eight entries" at "Size 2 M, 35 S", which adds up to 37. The list itself (737-917) holds 2 M and 36 S.
```

**Why it matters.** A count in the timeline that does not add up makes the reader distrust the other counts beside it.

**Done when.** Timeline row 1 gives v0.2.8's size as 2 M, 36 S, which matches its thirty-eight frozen entries.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. The timeline row's 2 M and 35 S were in `ROADMAP.md` at `817a4d88`, against a list holding 2 M and 36 S.

**Checked 2026-11-09:** timeline row 1 still reads "thirty-eight entries" with a Size of "2 M, 35 S". Counting the size marks in v0.2.8's frozen list gives 38 entries, 2 marked (M) and 36 marked (S).

**Generator check.** One-off: a finding from the `ROADMAP.md` structure-read sweep. The fact misread is whether one `ROADMAP.md` passage still agrees with a later record of the same thing. No head's `misread:` states that fact for `ROADMAP.md`, and the cluster came from one deliberate read rather than from a mechanism that keeps producing it.
