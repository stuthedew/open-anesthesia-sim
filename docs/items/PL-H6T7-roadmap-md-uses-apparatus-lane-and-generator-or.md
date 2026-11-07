---
id: PL-H6T7
title: ROADMAP.md uses apparatus, lane and generator (or generator head) throughout without saying what they mean, so a reader deciding a release cannot follow the rows that use them
priority: P3
effort: S
status: untriaged
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
deferred-from: v0.7.0 - filed after the gate froze; the roadmap's arrangement and wording, with no displayed value depending on it
added: 2026-11-07
---

**Problem.** ROADMAP.md uses apparatus, lane and generator (or generator head) throughout without saying what they mean, so a reader deciding a release cannot follow the rows that use them

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 50 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: the reader needs to know what three terms mean, and no chapter explains them. They are "apparatus" (version rows 65, 88, 94 and 95, explained only in passing at 3574-3581), "lane" (2254-2263, 5807-5829), and "generator" or "generator head" (310-315; version rows 107, 111, 113 and 114; 4784-4791; 7184-7196).
```

**Why it matters.** The version rows and the gate sections use these terms to say what a release holds. A reader who does not know them cannot follow those rows.

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.
