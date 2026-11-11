---
id: PL-K6DG
title: ROADMAP.md's Beyond row orders items 1-5, 9-10 and 13-15 by § "Development pathway", which also orders items 24 and 20 and item 8's scenario events, and item 30 places itself in Phase 1 but is on no row
priority: P2
effort: S
status: done
classes: defect, docs
feature: roadmap-structure
milestone: v0.6.17
touches: ROADMAP.md
added: 2026-11-07
closed: 2026-11-10
pr: 2085
payoff: A reader looking past v0.8.0 reads one order for the planned items, with item 30 placed where the owner put it.
verify: grep -qE '^\| (11|12\+) \|.*[^0-9.]30[^0-9]' ROADMAP.md
---

**Problem.** ROADMAP.md's Beyond row orders items 1-5, 9-10 and 13-15 by § "Development pathway", which also orders items 24 and 20 and item 8's scenario events, and item 30 places itself in Phase 1 but is on no row

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 61 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query (457, 8032-8035, 8792-8798): the Beyond row orders "Items 1-5, then 9 and 10, then 13-15, in § 'Development pathway' order", but the pathway also orders items 24 and 20 and item 8's scenario events. Item 30 places itself "Phase 1, ahead of the substance generalization". The timeline puts that generalization on row 11 (v0.8.0), and item 30 is on no row. The timeline governs (372-377), so the reader cannot tell whether item 30 comes before v0.8.0, or where items 20 and 24 fall.
```

**Why it matters.** Where the timeline names no release for an item, the pathway's order is the only guide to what comes next. Two orders, and an item on neither, leave the reader to guess. Item 30's half turns on where the substance generalization falls, which `PL-5XG1` already asks; this item is the rest of the order, not a second report of that question.

**Done when.** The Beyond row names every planned item it covers, items 20 and 24 included, in one order that matches § "Development pathway". Item 30 appears on the timeline row that the owner's placement of 2026-09-02 implies (Phase 1, ahead of the substance generalization), or the row says why it does not. Where the substance generalization itself falls stays with `PL-5XG1`.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. The Beyond row, the Phase 2 order and item 30's placement were all in `ROADMAP.md` at `817a4d88`.

**Checked 2026-11-09:** the Beyond row still orders items 1-5, 9-10 and 13-15 "in 'Development pathway' order". Phase 2 still orders item 24, then items 5, 3 and 4, then item 8's scenario events and item 20. Item 30 still says "Phase 1, ahead of the substance generalization" (project owner, 2026-09-02) and is on no timeline row. The record already holds each order, so placing the items to match it is a session's work.

**Generator check.** One-off: a finding from the `ROADMAP.md` structure-read sweep. The fact misread is whether one `ROADMAP.md` passage still agrees with a later record of the same thing. No head's `misread:` states that fact for `ROADMAP.md`, and the cluster came from one deliberate read rather than from a mechanism that keeps producing it.

**Done 2026-11-10.** The Beyond row now lists every item it covers in § "Development pathway" order: item 30; items 6 and 7 with the substance generalization; items 1 and 2; item 24; items 5, 3 and 4; item 8's scenario events and item 20; items 9 and 10; then items 13-15. It says item 30 comes first because the project owner placed it ahead of the generalization on 2026-09-02. Phase 1 in § "Development pathway" now names item 30 first too, so the two orders match, and its next paragraph says the generalization is the first half of item 6 and comes before nitrous oxide itself, item 7 and item 2, since item 30 now comes before the generalization. Where the generalization returns to a numbered row stays with the owner's condition in the Beyond row (`PL-5XG1`).
