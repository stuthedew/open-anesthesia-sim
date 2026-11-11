---
id: PL-2CL5
title: Three filings re-entered the misread fact 'whether the base already holds or has superseded a branch commit's change' after its fifth head closed (PL-JLK6, PL-N80K, PL-W5JR), so the fact is owed a sixth head or a recorded no-successor answer
priority: P2
effort: M
status: done
classes: defect
feature: landing-deletions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, docs/items
deferred-from: v0.7.0 - found 2026-11-11 after the freeze; apparatus, and it changes no displayed value, so the release does not wait on it
added: 2026-11-11
closed: 2026-11-11
pr: 2091
payoff: whether main took a branch's deletions gets the same single answer as its edits, so the next reader of that answer cannot leave deletions out
verify: grep -q '^class _LandingSplit' subprojects/docket/src/docket/vcs.py
root-cause-of: PL-TFF9, PL-N80K, PL-80SM, PL-HXYJ
generator: spent - _Landings.landing returns the content split and the deletion split as one _LandingSplit and the two separate methods are gone, so a reader cannot ask about content and leave deletions out; the deletion test reads what the base deleted since the fork, so it no longer decays
misread: Whether the base already holds or has superseded a branch commit's change, by whatever route
reenters: PL-927J
---

**Problem.** Three filings re-entered the misread fact 'whether the base already holds or has superseded a branch commit's change' after its fifth head closed (PL-JLK6, PL-N80K, PL-W5JR), so the fact is owed a sixth head or a recorded no-successor answer

**Checked 2026-11-11:** found by `PL-YSV3`, which made `bin/docket inflow` count re-entries per fact. Five heads state this fact in the same words: `PL-BHVM` and `PL-R808` (both filed 2026-09-12), `PL-GHHW` (2026-09-23), `PL-927J` and `PL-P813` (both 2026-09-27). The last of them closed on 2026-09-27. Three filings re-entered the fact after that date: `PL-JLK6` and `PL-N80K` (both filed 2026-10-18, `reenters: PL-927J`) and `PL-W5JR` (filed 2026-10-24, `reenters: PL-BHVM`). All three are done. Counted per named item, `PL-927J` had two and `PL-BHVM` had one, so neither line reached three. `bin/docket inflow` now lists the fact under `PL-BHVM` as "a generator whose fix did not hold", with seven filings in all.

**Why it matters.** `.claude/skills/docket/modes/triage.md` treats three filings after a head closed as a generator whose fix did not hold. This fact has had five root-cause items and is still being misread, and no open item holds the question.

**Done when.** One of two records exists, and `bin/docket inflow` no longer lists `PL-BHVM` under "a generator whose fix did not hold". Either a sixth head states the fact, with `root-cause-of:` naming the three filings and `reenters:` naming an earlier head, and says what the five earlier fixes left unread. Or an item records `no-successor:` against one of the five heads, and its brief says why the three filings are not one mechanism.

**Generator check.** Three post-close instances of a fact with five closed heads. Whether they share a mechanism the earlier fixes missed is the judgment this item asks for. It was not made here.

**Answer, 2026-11-11: a sixth head is owed, and this item is that head. It covers one of the three filings.** This is a session's judgment, so ordinary evidence reopens it. Read on this branch at `4a16024d3`.

- `PL-N80K` shares a mechanism with `PL-TFF9`, which re-entered `PL-GHHW` two days before `PL-927J` closed. `PL-927J` gave every reader one test of whether the base took a branch's change, `vcs._Landings`. That test reads the content the base wrote since the fork. A deletion writes no content, so the test could not see one. `PL-TFF9` added a second method for deletions, and each reader then had to combine the two answers itself. `orphaned` did so after `PL-TFF9`, and `_unlanded_refs` after `PL-N80K`. `_Landings.taken_whole`, which `claims` asks of a claim's commits, still did not (`PL-80SM`). The deletions method also tested the base's tip, so a merged deletion read as unmerged once a later commit wrote a file at that path (`PL-HXYJ`). Both were reproduced in a scratch repository before the fix.
- `PL-JLK6` is not a member. The landing test returned the right result there: the base had taken the branch whole. `Holdings.last` then left the branch's head commit out, which is a wrong consequence drawn from a correct result.
- `PL-W5JR` is not a member. The base's copy of the item file differed from the worker branch's copy because a review had sent the run back and edited the file. No comparison of content can read that decision. Its fix reads the run record, where the decision is written.

**What the five earlier heads left unread.** A deletion. Each fix asked what content the base holds, and a deletion has none.

**Done when, revised 2026-11-11.** The head's `root-cause-of:` names the items that share the mechanism, which are `PL-TFF9`, `PL-N80K`, `PL-80SM` and `PL-HXYJ`, not all three filings. `bin/docket inflow` lists `PL-BHVM` under the heading for lines answered by a successor.

**Built, 2026-11-11.** `_Landings.landing` returns one `_LandingSplit`, which holds the content split and the deletion split together, and its `whole` property reads both. The two separate methods are gone, so a reader cannot ask for one half. `_deleted_since` reads the deletions the base made since the fork, so a landed deletion stays landed. A branch that only deletes now reads as taken once the base deletes the same path. Before, it read as unlanded for as long as its ref lasted. `test_every_landed_reader_answers_from_the_branch_s_own_history` patches `landing`, so it still pins the three readers to one function.

**Searched 2026-11-11.** Among the items filed since 2026-09-28 whose `touches` name these readers, none filed after `PL-W5JR` (2026-10-24) states this fact.
