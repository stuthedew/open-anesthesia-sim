---
id: PL-1BVB
title: ROADMAP.md's planned-milestone catalogue still states six things other chapters contradict: item 8's unrecorded control changes, item 21's concentration history, item 1's open default flow and the three items waiting on it, and item 33's prerequisites and dark mode
priority: P3
effort: S
status: untriaged
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
---

**Problem.** ROADMAP.md's planned-milestone catalogue still states six things other chapters contradict: item 8's unrecorded control changes, item 21's concentration history, item 1's open default flow and the three items waiting on it, and item 33's prerequisites and dark mode

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 59 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: other chapters contradict several statements in the catalogue:
  - item 8, "Today the controller records concentrations but not why they moved" (8205-8220), though control changes have been recorded since v0.4.0 (1445-1468, 8037-8045);
  - item 21, "What remains is the controller's unbounded concentration history" (8306-8310), though v0.4.12 deleted that store (version row 77, 5235-5245);
  - item 1, which says the default flow's "value is open, under PL-NM7X" (8120-8130), though "The owner ruled on 2026-09-20 ... that 4.0 stays" (3016-3028);
  - item 1, "All three now wait on item 1 being implemented" (8132-8145), though PL-8PS6 cleared in Gate 1 (3472-3479, 5029-5044) and PL-WZVZ now waits on PL-TBMK and PL-4TWW (7015-7029);
  - item 33's "hard prerequisites" PL-7J96 and PL-2QMK (9042-9051), though PL-7J96 was dropped and PL-2QMK closed with v0.4.26's rendering tests (2053-2064, 2083-2084);
  - item 33's dark mode as "a separate decision" (9068-9074), which the light palette ratified on 2026-09-20, over a second dark palette, partly answers (version row 105, 4638-4650).
```

**Why it matters.** A reader choosing what to build next reads the catalogue for what is still wanted. Each of these statements says that work remains, or that a decision is open, where another chapter records that it was done or decided. The rest of the catalogue finding, which moves the shipped records out, is slice 7 (`PL-M3MV`).

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The rest of the v0.4.12 row (row 77) is now in `PL-R3Y3`'s brief, and the rest of the v0.5.4 row (row 105) in `PL-4KSZ`'s.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. All six statements were in `ROADMAP.md` at `817a4d88`, in their wording before the plain-English rewrite of 2026-10-25 (`a859be00`), and so were the passages they contradict.
