---
id: PL-HXJJ
title: ROADMAP.md's baseline and version rows test each patch against both halves, or one half, of § "Versioning decision"'s test, which names no halves
priority: P3
effort: S
status: untriaged
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
deferred-from: v0.7.0 - filed after the gate froze; the roadmap's arrangement and wording, with no displayed value depending on it
added: 2026-11-07
---

**Problem.** ROADMAP.md's baseline and version rows test each patch against both halves, or one half, of § "Versioning decision"'s test, which names no halves

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 51 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: 279-286 calls v0.6.16 "a patch on both halves of § 'Versioning decision''s test", and version rows 99 and 100 say "both halves" and "one half only". § "Versioning decision" (15-35) names no two halves.
```

**Why it matters.** A reader checking why a release took a patch number looks for the test those rows apply, and § "Versioning decision" names no halves.

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The v0.4.34 and v0.4.35 rows (rows 99 and 100) are now in `PL-Y3XK`'s and `PL-F1SZ`'s briefs. The baseline's "both halves" is unchanged.
