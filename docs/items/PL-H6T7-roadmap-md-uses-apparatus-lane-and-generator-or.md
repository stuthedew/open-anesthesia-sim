---
id: PL-H6T7
title: ROADMAP.md uses apparatus, lane and generator (or generator head) throughout without saying what they mean, so a reader deciding a release cannot follow the rows that use them
priority: P3
effort: S
status: ready
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
payoff: The owner deciding a release can follow the rows that say it closed a generator head or touched the apparatus.
verify: grep -qE '^#{2,4} Terms' ROADMAP.md
---

**Problem.** ROADMAP.md uses apparatus, lane and generator (or generator head) throughout without saying what they mean, so a reader deciding a release cannot follow the rows that use them

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 50 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: the reader needs to know what three terms mean, and no chapter explains them. They are "apparatus" (version rows 65, 88, 94 and 95, explained only in passing at 3574-3581), "lane" (2254-2263, 5807-5829), and "generator" or "generator head" (310-315; version rows 107, 111, 113 and 114; 4784-4791; 7184-7196).
```

**Why it matters.** The version rows and the gate sections use these terms to say what a release holds. A reader who does not know them cannot follow those rows.

**Done when.** `ROADMAP.md` has a short section near the top, headed "Terms this file uses", that defines apparatus, lane, generator and generator head in plain words. The other undefined terms that `PL-71H3`, `PL-NTHF` and `PL-YRY3` list can be added to the same section.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The rest of rows 65, 88, 94 and 95 (v0.4.0, v0.4.23, v0.4.29 and v0.4.30) is now in `PL-647D`'s, `PL-2YSL`'s, `PL-GL5P`'s and `PL-SW0D`'s briefs. Row 107's (v0.5.6) use of "generator" is now in `PL-38HD`'s brief. Rows 111, 113 and 114 still say "generator head" in the sentence each keeps in the table.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. "apparatus", "lane" and "generator" were used without definition at `817a4d88`. Two of the places the item cites were added later (`720d23be`, `6ffbf794`, `d1196bdb`).

**Checked 2026-11-09:** `grep -n -i apparatus ROADMAP.md` finds 19 uses and no definition. "Generator head" appears in § "Current baseline" and in the v0.5.8 to v0.5.13 rows, undefined. "Lane" is explained in § "Recording it" (the product and workflow lanes share no files), but not where the word first appears.

**Generator check.** One-off: a finding from the `ROADMAP.md` structure-read sweep. The fact misread is whether one `ROADMAP.md` passage still agrees with a later record of the same thing. No head's `misread:` states that fact for `ROADMAP.md`, and the cluster came from one deliberate read rather than from a mechanism that keeps producing it.
