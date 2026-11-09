---
id: PL-392N
title: ROADMAP.md gives a 30-day case's control timeline as about 140 KiB against 3.16 GB in v0.4.0's section, and about 70 KiB at 50 changes a day in the v0.4.8 version row
priority: P3
effort: S
status: dropped
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
closed: 2026-11-09
reason: Both figures left ROADMAP.md in the restructure and now sit only in closed briefs (PL-GS5X, PL-Y5WR, PL-T691), which are records; PL-T691 gives the 30-day case as about 70 KiB of control events plus about 70 KiB of keyframes, so the 140 KiB and the 70 KiB are one sum and do not disagree. PL-VM1Q question 12 asks how the figure was obtained.
---

**Problem.** ROADMAP.md gives a 30-day case's control timeline as about 140 KiB against 3.16 GB in v0.4.0's section, and about 70 KiB at 50 changes a day in the v0.4.8 version row

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 56 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: a 30-day case kept as a control timeline is "about 140 KiB ... against 3.16 GB" at 1509-1519, but "~70 KiB vs 3.16 GB ... at 50 changes/day" in version row 73.
```

**Why it matters.** The size of a 30-day case's control timeline was the ground for keeping it as a timeline. The two figures differ by a factor of two.

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The v0.4.8 row's figure is now in `PL-BKDP`'s brief.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. The 140 KiB and 3.16 GB figures and the v0.4.8 row's 70 KiB were both in `ROADMAP.md` at `817a4d88`.

**Checked 2026-11-09:** `grep -n 'KiB\|3\.16' ROADMAP.md` finds both figures only in this item's own title on v0.7.0's frozen list. The restructure moved the passages out. The 140 KiB is now in the briefs of `PL-GS5X`, `PL-Y5WR` and `PL-T691`, and the 70 KiB in `PL-T691`'s, all closed. `PL-T691` gives the 30-day case as about 70 KiB of control events plus about 70 KiB of keyframes, so the two figures are one sum and do not disagree.

**Generator check.** None owed: the fault no longer exists, so the item is dropped.
