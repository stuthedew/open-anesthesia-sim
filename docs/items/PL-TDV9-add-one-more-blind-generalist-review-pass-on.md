---
id: PL-TDV9
title: Add one more blind generalist review pass on each simulator pull request: in PL-TCBJ's replay one generalist caught the later-filed defect in 5 of 10 merged pull requests, as many as a three-specialist panel at a third of the cost
status: untriaged
feature: review-panel
blocked-by: PL-TBQS
added: 2026-10-24
---

**Problem.** Add one more blind generalist review pass on each simulator pull request: in PL-TCBJ's replay one generalist caught the later-filed defect in 5 of 10 merged pull requests, as many as a three-specialist panel at a third of the cost

**Evidence.** `PL-TCBJ` replayed reviews on ten merged simulator pull requests that later had a defect filed against them. Three specialist reviewers (PK/PD, numerics and state, clinical display) caught the later defect in 4 of 10. One generalist reviewer with the same brief, run blind in a clean directory, caught it in 5 of 10, and named 8 of the 20 key defects to the panel's 7. The rule fixed before the count was that a generalist catching as many means one more pass, not a panel. A blind checker marked 59 of the panel's 62 findings correct and none incorrect.

**What it would be.** One subagent per simulator pull request, at the session's own model and effort, given only the tree at the head commit and the diff, with the brief `PL-TCBJ` used: review the whole diff, report at most eight findings in the form `### F<n> [blocking|should-fix|optional] <file> :: <symbol>`, and report only what it would defend to the author. Its findings go where review findings already go. The brief text is in `PL-TCBJ` under "The reviewer brief, as run".

**Cost.** Each replay review used about 150,000 to 300,000 subagent tokens and 5 to 15 minutes. Ten pull requests cannot show the generalist better than the panel or the reverse; they show that one extra blind pass finds about half of what later gets filed.

**Before building.** This is a new workflow mechanism. `CLAUDE.md` § "What this project is" pauses new workflow mechanisms while a workflow-lane item carries `generator: live`, so check `bin/docket generators` first.

**Held for a larger sample, 2026-10-24.** The project owner asked for a larger test before choosing between the panel and a generalist pass. So this item is not built until that test reports.

- The pool limits the sample. `PL-TCBJ`'s protocol found 73 candidate pull requests, excluded one, examined 39 and verified 10. At that rate the other 33 hold about 8 or 9 more, so the whole pool is about 18 or 19 pull requests.
- At that size a test can show only a large difference. In `PL-TCBJ`, 3 of the 10 pull requests were caught by one arm and not the other. At that rate, an exact paired test (McNemar) at two-sided 5% detects an arm that wins 3 of every 4 such pull requests 9% of the time with 19 pull requests, 31% with 40 and 75% with 100. These figures come from exact binomial enumeration, run in the session that wrote this paragraph.
- The comparison also mixed two things. The panel ran three reviews and the control ran one, so the panel's catches could come from more draws rather than from specialism.

**Recommendation:** run the rest of the pool, about 9 more pull requests, and add two more generalist runs on every pull request. That gives one-generalist, three-generalist and panel results on the same diffs, and the three-generalist arm costs the same as the panel. Score each key defect as well as each pull request. Fix the bar before the count. Build the panel only if it names at least 3 more key defects than three generalist runs. Otherwise build generalist passes, with a second pass only if runs 2 and 3 together name at least 3 key defects that run 1 missed. The cost is about 74 new reviews at 150,000 to 300,000 subagent tokens each, so 11 to 22 million tokens, plus verifying the other candidates and one blind checker per pull request. Seeding planted defects to grow the sample past the pool is not recommended, because it measures how reviewers find planted faults rather than the faults this project ships.

**Decision** (project owner, 2026-10-24, ratified, over choosing on `PL-TCBJ`'s ten pull requests, over running the rest of the pool with one generalist only, and over seeded defects). The larger test runs as recommended above. It is `PL-TBQS` (the larger replay of the reviewer test), which holds the protocol and the bar fixed before the count. This item is built, or dropped for the panel, on that item's result.

**The larger replay chose two passes, 2026-10-24.** `PL-TBQS` (the larger replay of the reviewer test) ran the rest of the pool, 20 merged pull requests and 39 key defects, with one-generalist, three-generalist and panel arms on every pull request, scored blind. The panel named 19 key defects and three generalist runs named 21. That is short of the 3 more the panel needed, so its bar chose generalist passes over the panel. Runs 2 and 3 together named 3 key defects that run 1 missed, which meets the threshold for a second pass exactly. So the build this item describes is two blind generalist passes on each simulator pull request, not one; the title still says one because `bin/docket set` cannot change a title. The second pass rests on exactly 3 defects. One of them, `#376`'s `PL-2MD9`, was a close call the scorer made blind, and without it the bar would have chosen one pass. `PL-TBQS`'s Result has the table and the limitations. The hold above is lifted. `CLAUDE.md`'s pause on new workflow mechanisms still applies, so check `bin/docket generators` before building.
