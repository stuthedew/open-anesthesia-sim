---
id: PL-K6DG
title: ROADMAP.md's Beyond row orders items 1-5, 9-10 and 13-15 by § "Development pathway", which also orders items 24 and 20 and item 8's scenario events, and item 30 places itself in Phase 1 but is on no row
priority: P3
effort: S
status: untriaged
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
---

**Problem.** ROADMAP.md's Beyond row orders items 1-5, 9-10 and 13-15 by § "Development pathway", which also orders items 24 and 20 and item 8's scenario events, and item 30 places itself in Phase 1 but is on no row

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 61 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query (457, 8032-8035, 8792-8798): the Beyond row orders "Items 1-5, then 9 and 10, then 13-15, in § 'Development pathway' order", but the pathway also orders items 24 and 20 and item 8's scenario events. Item 30 places itself "Phase 1, ahead of the substance generalization". The timeline puts that generalization on row 11 (v0.8.0), and item 30 is on no row. The timeline governs (372-377), so the reader cannot tell whether item 30 comes before v0.8.0, or where items 20 and 24 fall.
```

**Why it matters.** Where the timeline names no release for an item, the pathway's order is the only guide to what comes next. Two orders, and an item on neither, leave the reader to guess. Item 30's half turns on where the substance generalization falls, which `PL-5XG1` already asks; this item is the rest of the order, not a second report of that question.

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. The Beyond row, the Phase 2 order and item 30's placement were all in `ROADMAP.md` at `817a4d88`.
