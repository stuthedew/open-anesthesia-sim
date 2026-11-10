---
id: PL-HXJJ
title: ROADMAP.md's baseline and version rows test each patch against both halves, or one half, of § "Versioning decision"'s test, which names no halves
priority: P3
effort: S
status: done
classes: defect, docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
closed: 2026-11-10
pr: 2083
payoff: A reader checking why a release took a patch number finds the two-part test the baseline and the cut items apply.
verify: grep -qiE 'test has two (halves|parts)' ROADMAP.md
recurrences: 2026-11-07 PL-V82M
---

**Problem.** ROADMAP.md's baseline and version rows test each patch against both halves, or one half, of § "Versioning decision"'s test, which names no halves

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 51 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: 279-286 calls v0.6.16 "a patch on both halves of § 'Versioning decision''s test", and version rows 99 and 100 say "both halves" and "one half only". § "Versioning decision" (15-35) names no two halves.
```

**Why it matters.** A reader checking why a release took a patch number looks for the test those rows apply, and § "Versioning decision" names no halves.

**Done when.** § "Versioning decision" says that the patch test has two halves and names them: the release crosses no capability boundary, and every higher number is already given to a milestone section. Each passage that tests a patch against "both halves" or "one half" then refers to those names.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The rest of the v0.4.34 and v0.4.35 rows (rows 99 and 100) is now in `PL-Y3XK`'s and `PL-F1SZ`'s briefs. The baseline's "both halves" is unchanged.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. The baseline's "both halves" test and the version rows' "one half" were in `ROADMAP.md` at `817a4d88`, and § "Versioning decision" named no halves.

**Checked 2026-11-09:** § "Current baseline" still calls v0.6.16 "a patch on both halves of § 'Versioning decision''s test", and § "Versioning decision" names no halves. The moved v0.4.34 and v0.4.35 rows in `PL-Y3XK`'s and `PL-F1SZ`'s briefs show what the halves are: no capability boundary is crossed, and every higher number is already given to a milestone section. Those are the section's capability-boundary rule and its paragraph "Which numbers a patch cut may take". The tree answers the question, so the fix is a session's.

**Generator check.** One-off: a finding from the `ROADMAP.md` structure-read sweep. The fact misread is whether one `ROADMAP.md` passage still agrees with a later record of the same thing. No head's `misread:` states that fact for `ROADMAP.md`, and the cluster came from one deliberate read rather than from a mechanism that keeps producing it.

**Done 2026-11-10.** § "Versioning decision" now has a paragraph, "The two halves of the patch test", that names them: the release crosses no capability boundary, and the next minor number is already given to a milestone section. It says what a patch on one half only means. The baseline's "both halves" now names both. The other uses of "one half" were in version rows that moved to closed cut briefs, which are records and are left as they are.
