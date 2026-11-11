---
id: PL-LVN8
title: Decide whether ROADMAP.md moves its decision history to the items, starting with each release's long version-table entry and v0.5.0's 2,000 rows of gate dispositions, and keeps one line for each
status: done
feature: roadmap-structure
milestone: v0.6.17
touches: ROADMAP.md, .claude/skills/docket/modes/release.md
added: 2026-11-07
closed: 2026-11-07
pr: 2060
verify: grep -q 'A version-table row is one sentence' .claude/skills/docket/modes/release.md
---

**Problem.** Decide whether ROADMAP.md moves its decision history to the items, starting with each release's long version-table entry and v0.5.0's 2,000 rows of gate dispositions, and keeps one line for each

**Source.** The copy editor's structure read of `ROADMAP.md`, run on the project owner's Mac on 2026-11-06: one read per chapter, then one read of all the chapters' outlines together. Row numbers are `ROADMAP.md` at `aff76df1`, the last commit to change it before slice 1 (`PL-W0TS`), so a later slice finds each passage by the words the finding quotes. The project owner chose to file the findings as items and apply them one slice per pull request (project owner, 2026-11-07, ratified, over one pull request for the whole restructure), because the release tools read the roadmap's gate sections and a small move is easier to check against them. The raw reads are in the project's shared folder, `/mnt/project-files/v0.7.0/repo-copy-edit/mac-structure-reads/ROADMAP-md/structure/`.

**The question.** Should the roadmap move its decision history into the items, and keep one line for each record? The outline read leaves the largest block to the project owner (finding 10), and chapter read 2 says the same of the version table:

- Written for another reader, an owner's decision (3221-5219): about 2,000 rows record Gate 1's dispositions item by item, and the reader deciding a release does not act on them. v0.6.0 moved its own 43 such records onto the items on 2026-09-23 (6409-6413). § "Recording it" says completed sections keep these subsections (7885-7905), so moving them to the items or to a history file is the project owner's call.
- Rows 48–160 (written for another reader; writing rule pattern 5 across the whole table): from v0.2.6 on, the cells use internal tool, check and item names that this reader does not know (`bin/docket`, `doc_check`, `verify:`, `PL-` ids, "generator head", "frozen list", "the cut"). They record how each claim was checked (tree hashes, syntax-tree comparisons, counts of sampled states) and who decided what ("project owner, 2026-09-22, ratified, over …"). Rows 68, 88 and 89 each run past a thousand words. That material belongs in the release notes under `docs/releases/` and in the items. Each cell should keep one sentence on what a learner can now do or see, and whether the model changed, plus a pointer to the release note.

**What is there now** (counted with `wc -w` at `aff76df1`). The version table, rows 37-160, holds 44,788 words, and each release cut adds a row. v0.5.0's gate dispositions, rows 3221-5219, hold 23,792 words. The whole file is 159,824 words. The chapter reads find more decision history in most other sections, in smaller blocks.

**The two rules that disagree.** § "Recording it" says of the `Declined`, `Deferred` and `Sequenced` subsections: "Completed sections keep those subsections, because they are the record of that period." `.claude/rules/plain-writing.md` says, for every document it covers, `ROADMAP.md` among them: "Decision history goes in the item." No rule asks the version table for more than a release's version, status and milestone, and the release procedure writes the long rows.

**The options.**

1. Move both blocks to the items, and keep one line each in the roadmap. Each version row keeps one sentence on what the release changed for a learner, with its item count. The rest of the row moves to the release's cut item, and the release procedure then writes one sentence per row. Each disposition moves to its item's brief as a dated paragraph, and the roadmap keeps one line per ground with the ids. The other sections' smaller blocks move the same way as each slice reaches them. The roadmap falls from about 160,000 words to about 95,000.
2. Move v0.5.0's dispositions only. The version table keeps its long rows.
3. Keep both. The slices change only the order and the repeats.

**Recommended: option 1.** The reader of the roadmap is deciding what a release holds, and these records do not change that decision. The writing rule already puts decision history in the item, and v0.6.0 moved its own 43 disposition records onto its items on 2026-09-23. The record is kept whole, in the item it concerns, so nothing is lost. The cost is 122 version rows and about 135 item briefs edited (one per disposition entry), inside slices 3 (`PL-DWGC`) and 9 (`PL-4BCF`), and one change to the release procedure, which the project owner's request covers. With option 3, each cut keeps adding a row of about 300 to 1,000 words.

**Why the choice is the owner's.** It reverses a sentence of § "Recording it" and changes what every later release cut writes, and the outline read names it the owner's call.

**Done when.** The answer is recorded below this question, with its date. Slices 3 (`PL-DWGC`) and 9 (`PL-4BCF`) carry it out, and their items record the answer.

**Answer: option 1, move both (project owner, 2026-11-07, ratified, over moving only v0.5.0's dispositions and over keeping both).** He chose it on the decision card at 20:10 UTC. Each version row keeps one sentence on what the release changed for a learner, with its item count, and the rest of the row moves to the release's cut item. Each v0.5.0 disposition moves to its item's brief as a dated paragraph, and the roadmap keeps one line per ground with the ids. The release procedure's change took effect the same day: `.claude/skills/docket/modes/release.md` now says a version-table row is one sentence. The sentence of § "Recording it" that keeps completed sections' dispositions as the record of their period is reversed in slice 9.

**Generator check.** A question for the project owner, answered here. No mechanism produced it, so nothing is recorded as a generator.
