---
id: PL-9857
title: ROADMAP.md's v0.6.0 section says Gate 2's frozen list has not yet been checked for stale entries, while the v0.5.1 version row says Gate 2's 168 clearable entries were swept
priority: P3
effort: S
status: untriaged
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
---

**Problem.** ROADMAP.md's v0.6.0 section says Gate 2's frozen list has not yet been checked for stale entries, while the v0.5.1 version row says Gate 2's 168 clearable entries were swept

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 20 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- The staleness sweep: "one measured pass found 12 of 134 items dead and 31 more overtaken" (6036-6044) and "found 12 of 134 open items dead and 31 more overtaken, 32% in all" (7732-7755). The figure belongs in § "The cadence". v0.6.0 keeps whether and when its own list was swept. Query: 6036-6044 says Gate 2's list "has not yet been checked for stale entries", but version row 102 (v0.5.1) says "Gate 2's 168 clearable entries swept".
```

**Why it matters.** Whether Gate 2's list was swept for stale entries says how far its count can be trusted. The two passages give opposite answers. The rest of the finding, where the staleness figure belongs, is slice 2 (`PL-P0C5`).

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The v0.5.1 row's sweep figure is now in `PL-V065`'s brief.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. The "not swept for staleness yet" paragraph and the v0.5.1 row saying Gate 2's list was swept were both in `ROADMAP.md` at `817a4d88`.
