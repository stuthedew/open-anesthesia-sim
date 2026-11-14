---
id: PL-40ZB
title: PL-04KR's predictions missed three times for 2026-11-02..11-08, as v0.6.17's cut reported: 40 new apparatus paths over 111 filings (0.36 a filing against the 0.13 ceiling, 11 the week before), 12 P1 workflow-lane apparatus filings whose band no rank or owner set, and 14 re-entries against 4; find what generated each
priority: P2
effort: M
status: ready
classes: infra
feature: convergence-visibility
touches: docs/items
added: 2026-11-11
payoff: the work that keeps apparatus inflow from falling is found and named, so it can be stopped
verify: grep -qE '^\*\*What generated each miss\.\*\*' docs/items/PL-40ZB*.md
not-delegable: naming a generator is judgment, and the command proves only that the verdicts were written
sweep: what generated each of the three PL-04KR misses in the week of 2026-11-02
---

**Problem.** PL-04KR's predictions missed three times for 2026-11-02..11-08, as v0.6.17's cut reported: 40 new apparatus paths over 111 filings (0.36 a filing against the 0.13 ceiling, 11 the week before), 12 P1 workflow-lane apparatus filings whose band no rank or owner set, and 14 re-entries against 4; find what generated each

**Why it matters.** `PL-04KR` pre-registered the owner's expectation that apparatus inflow falls now that the workflow is built. `CLAUDE.md` § "What this project is" says that a miss means something is generating work, and that it should be found. Three predictions missed in one week, after one miss the week before. Each miss left unexplained may be a generator that goes on filing items.

**Done when.** This brief names, for each of the three misses, what generated it: a new head recorded with `root-cause-of:`, `generator:` and `misread:`; an existing head whose fix did not hold, recorded on the members with `--reenters`; or the reason it is not a generator. The verdicts sit under a heading "**What generated each miss.**"

**Generator check.** This item is the search for generators, so it is not itself a member of one.
