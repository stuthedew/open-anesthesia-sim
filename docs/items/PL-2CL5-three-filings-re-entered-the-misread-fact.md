---
id: PL-2CL5
title: Three filings re-entered the misread fact 'whether the base already holds or has superseded a branch commit's change' after its fifth head closed (PL-JLK6, PL-N80K, PL-W5JR), so the fact is owed a sixth head or a recorded no-successor answer
status: untriaged
added: 2026-11-11
---

**Problem.** Three filings re-entered the misread fact 'whether the base already holds or has superseded a branch commit's change' after its fifth head closed (PL-JLK6, PL-N80K, PL-W5JR), so the fact is owed a sixth head or a recorded no-successor answer

**Checked 2026-11-11:** found by `PL-YSV3`, which made `bin/docket inflow` count re-entries per fact. Five heads state this fact in the same words: `PL-BHVM` and `PL-R808` (both filed 2026-09-12), `PL-GHHW` (2026-09-23), `PL-927J` and `PL-P813` (both 2026-09-27). The last of them closed on 2026-09-27. Three filings re-entered the fact after that date: `PL-JLK6` and `PL-N80K` (both filed 2026-10-18, `reenters: PL-927J`) and `PL-W5JR` (filed 2026-10-24, `reenters: PL-BHVM`). All three are done. Counted per named item, `PL-927J` had two and `PL-BHVM` had one, so neither line reached three. `bin/docket inflow` now lists the fact under `PL-BHVM` as "a generator whose fix did not hold", with seven filings in all.

**Why it matters.** `.claude/skills/docket/modes/triage.md` treats three filings after a head closed as a generator whose fix did not hold. This fact has had five root-cause items and is still being misread, and no open item holds the question.

**Done when.** One of two records exists, and `bin/docket inflow` no longer lists `PL-BHVM` under "a generator whose fix did not hold". Either a sixth head states the fact, with `root-cause-of:` naming the three filings and `reenters:` naming an earlier head, and says what the five earlier fixes left unread. Or an item records `no-successor:` against one of the five heads, and its brief says why the three filings are not one mechanism.

**Generator check.** Three post-close instances of a fact with five closed heads. Whether they share a mechanism the earlier fixes missed is the judgment this item asks for. It was not made here.
