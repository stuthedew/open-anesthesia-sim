---
id: PL-TDV9
title: Add one more blind generalist review pass on each simulator pull request: in PL-TCBJ's replay one generalist caught the later-filed defect in 5 of 10 merged pull requests, as many as a three-specialist panel at a third of the cost
status: untriaged
feature: review-panel
added: 2026-10-24
---

**Problem.** Add one more blind generalist review pass on each simulator pull request: in PL-TCBJ's replay one generalist caught the later-filed defect in 5 of 10 merged pull requests, as many as a three-specialist panel at a third of the cost

**Evidence.** `PL-TCBJ` replayed reviews on ten merged simulator pull requests that later had a defect filed against them. Three specialist reviewers (PK/PD, numerics and state, clinical display) caught the later defect in 4 of 10. One generalist reviewer with the same brief, run blind in a clean directory, caught it in 5 of 10, and named 8 of the 20 key defects to the panel's 7. The rule fixed before the count was that a generalist catching as many means one more pass, not a panel. A blind checker marked 59 of the panel's 62 findings correct and none incorrect.

**What it would be.** One subagent per simulator pull request, at the session's own model and effort, given only the tree at the head commit and the diff, with the brief `PL-TCBJ` used: review the whole diff, report at most eight findings in the form `### F<n> [blocking|should-fix|optional] <file> :: <symbol>`, and report only what it would defend to the author. Its findings go where review findings already go. The brief text is in `PL-TCBJ` under "The reviewer brief, as run".

**Cost.** Each replay review used about 150,000 to 300,000 subagent tokens and 5 to 15 minutes. Ten pull requests cannot show the generalist better than the panel or the reverse; they show that one extra blind pass finds about half of what later gets filed.

**Before building.** This is a new workflow mechanism. `CLAUDE.md` § "What this project is" pauses new workflow mechanisms while a workflow-lane item carries `generator: live`, so check `bin/docket generators` first.
