---
id: PL-8G3F
title: ROADMAP.md's v0.7.0 frozen-list headings count 9 + 82 = 91 entries, while the baseline and the v0.6.16 version row put Gate 3 at 87 of 90 cleared
priority: P2
effort: S
status: untriaged
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
deferred-from: v0.7.0 - filed after the gate froze; the roadmap's arrangement and wording, with no displayed value depending on it
added: 2026-11-07
---

**Problem.** ROADMAP.md's v0.7.0 frozen-list headings count 9 + 82 = 91 entries, while the baseline and the v0.6.16 version row put Gate 3 at 87 of 90 cleared

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 54 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: v0.7.0's list headings give 9 + 82 = 91 entries (7076, 7088), but 288-291 and version rows 159-160 put Gate 3 at "87 of 90".
```

**Why it matters.** The gate count is how the roadmap says how close v0.7.0 is to being cut. Two counts of the same list disagree by one entry.

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The v0.6.15 and v0.6.16 rows' gate counts are now in `PL-8B6Z`'s and `PL-80PZ`'s briefs. The baseline's copy is unchanged.
