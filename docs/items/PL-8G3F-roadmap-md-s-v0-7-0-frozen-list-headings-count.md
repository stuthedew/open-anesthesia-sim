---
id: PL-8G3F
title: ROADMAP.md's v0.7.0 frozen-list headings count 9 + 82 = 91 entries, while the baseline and the v0.6.16 version row put Gate 3 at 87 of 90 cleared
priority: P2
effort: S
status: done
classes: defect, docs
feature: roadmap-structure
milestone: v0.6.17
touches: ROADMAP.md
deferred-from: v0.7.0 - a new problem: the list's headings and the baseline's count first disagreed when aff76df1 (2026-11-05) added PL-0P3F, after the freeze
added: 2026-11-07
closed: 2026-11-10
pr: 2082
payoff: A reader judging how close v0.7.0 is to its cut reads one Gate 3 count, not 87 of 90 beside a list of 127.
verify: ! grep -qF 'The gate stands at 87 of 90 cleared' ROADMAP.md
---

**Problem.** ROADMAP.md's v0.7.0 frozen-list headings count 9 + 82 = 91 entries, while the baseline and the v0.6.16 version row put Gate 3 at 87 of 90 cleared

**Found by** the copy editor's structure read of `ROADMAP.md` (2026-11-06), finding 54 of its outline read. Rows are `ROADMAP.md` at `aff76df1`, before the restructure's first slice (`PL-W0TS`) moved its sections; the quoted words find each passage after the move. The finding is quoted whole, as a block.

```text
- Query: v0.7.0's list headings give 9 + 82 = 91 entries (7076, 7088), but 288-291 and version rows 159-160 put Gate 3 at "87 of 90".
```

**Why it matters.** The gate count is how the roadmap says how close v0.7.0 is to being cut. Two counts of the same list disagree by one entry.

**Done when.** The roadmap gives one answer, taken from the tree where the tree holds it and from the project owner where it does not, and every passage that stated the other answer is corrected.

**Where the quoted row text is now (2026-11-07).** `PL-DWGC` keeps one sentence in each version-table row and moves the rest of the row, word for word, to the release's cut item, which the table's Details column names. The v0.6.15 and v0.6.16 rows' gate counts are now in `PL-8B6Z`'s and `PL-80PZ`'s briefs. The baseline's copy is unchanged.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem began after Gate 3 froze at `817a4d88`, so the item stays deferred to the next gate, and its `deferred-from:` names the commit that began it. At `817a4d88` the headings read 9 and 37 entries, and no "87 of 90" existed. `f369249f` (2026-11-04) wrote "87 of 90", and `aff76df1` (2026-11-05) raised the heading to 82, which made the two disagree.

**Checked 2026-11-09:** § "Current baseline" still says "The gate stands at 87 of 90 cleared, as at the v0.6.15 tag", and names `PL-SP6H` as the only entry this gate can still clear. v0.7.0's list headings now read 9 and 118 entries, 127 in all, after `PL-GW0P` re-admitted the findings present at the freeze. The v0.6.16 cut (`720d23be`) wrote the count 38 minutes before `aff76df1` added an entry. § "Recording it" allows a count dated to a release, but this one is written in the present tense and its account of what is still open is no longer true.

**Generator check.** One-off. The fact is how many entries a gate's frozen list holds and how many have cleared, which is near `PL-J6HP`'s (gate facts held in `ROADMAP.md` prose). This is a count dated to a release that § "Recording it" permits, gone stale in its tense, so it is not a re-entry of that head.

**Done 2026-11-10.** § "Current baseline" now dates its count: when v0.6.16 was cut, 87 of the gate's 90 entries had cleared, which `ROADMAP.md` at the v0.6.16 tag confirms (headings of 9 and 81 entries). It says that `PL-GW0P` lengthened the list on 2026-11-07, and it points at the two headings under v0.7.0 for the size instead of restating it. The sentences naming `PL-SP6H` as still open went with it. No other passage in `ROADMAP.md` gives 87 of 90.
