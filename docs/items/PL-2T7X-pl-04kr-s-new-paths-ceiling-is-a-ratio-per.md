---
id: PL-2T7X
title: PL-04KR's new-paths ceiling is a ratio per filing, so it rises when filings fall: 2026-10-26..11-01 named 11 new apparatus paths, down from 34, over 19 filings, down from 117, and reads 0.58 against the 0.13 ceiling, flagging converging inflow as growth
priority: P2
effort: S
status: done
classes: defect
feature: convergence-visibility
milestone: v0.6.15
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md, docs/items/PL-2T7X-pl-04kr-s-new-paths-ceiling-is-a-ratio-per.md, docs/items/PL-04KR-pre-register-the-apparatus-convergence.md
deferred-from: v0.7.0 - filed after the gate froze; an apparatus-only release-report fix with no effect on what a learner sees, worked and closed on its own branch
added: 2026-11-03
closed: 2026-11-03
pr: 1977
payoff: a release cut stops reporting apparatus growth in a week when fewer new apparatus files appeared than the week before, so a falling filing count no longer costs an investigation item
verify: grep -q 'def test_the_new_paths_ceiling_breaks_only_when_the_count_did_not_fall' subprojects/docket/tests/test_inflow.py
---

**Problem.** PL-04KR's new-paths ceiling is a ratio per filing, so it rises when filings fall: 2026-10-26..11-01 named 11 new apparatus paths, down from 34, over 19 filings, down from 117, and reads 0.58 against the 0.13 ceiling, flagging converging inflow as growth

**Measured 2026-11-03** by `PL-CK1W`'s verdict, with `docket.inflow.analyze` on `main` at `4620917c`. New apparatus paths by week: 30 (2026-10-12 to 10-18), 34 (10-19 to 10-25), 11 (10-26 to 11-01). Filings over the same weeks: 107, 117 and 19. `bin/docket inflow` and `docket.inflow.missed` report the last week as "11 new apparatus paths over 19 filings, 0.58 a filing, above the 0.13 ceiling: the surface is still growing". The count of new paths fell by two thirds, so the surface grew more slowly, not faster.

**Why it matters.** `CLAUDE.md` § "What this project is" expects apparatus inflow to decline now that the functionality is settled. A ratio per filing rises whenever filings fall faster than new paths, so the check reads the expected decline as a broken prediction, and each such week costs an investigation item like `PL-CK1W`. The same week also reports one `P1` filing outside the generator tier, `PL-D59R`, which is a separate prediction.

**Done when.** The new-paths prediction is stated in a form that a falling filing count cannot break on its own, such as an absolute count per week or a ratio read only above a minimum number of filings, and `docket.inflow.missed` reads it that way. `PL-04KR` pre-registered the prediction, so the change records why the restatement is not moving the goalposts.

**Generator check.** One-off. The fact misread is what the new-paths prediction measures: the ratio per filing stood in for the growth of the surface, and only this check reads it. `PL-00TR`, the other false alarm in the same check, misread a different fact (a band that records a class pin rather than a severity), so the two share a file and not a mechanism.

**Restated form, and why it does not move the goalposts.** Decided 2026-11-03 by the session that built it, as the brief's "such as" leaves to the session. The 0.13 ceiling still applies, but a week breaks it only when its count of new paths is at least the count of the complete week before it. A first complete week has no week before it and is read against the ceiling alone. Two other forms were weighed and refused:

1. **A ratio read only above a minimum number of filings.** The minimum would be chosen after seeing this week's 19 filings, so any threshold above 19 is fitted to the one week it excuses. Choosing a number after the outcome is what pre-registration exists to stop.
2. **An absolute ceiling on new paths per week, taken from the baseline.** `PL-04KR` recorded only the ratios, not the counts. Over today's store the baseline weeks read 0.63, 0.19, 0.23 and 0.15, because the store and the week anchor have both moved since 2026-09-19, so any count picked now would also be chosen after the outcome. It would also tighten the prediction: a busy week with a low ratio, which the pre-registered form passes, could break an absolute count.

The chosen form keeps the pre-registered number and relaxes it only where the count of new paths fell, which is the convergence `PL-04KR` expects. It is the same comparison with the week before that the re-entry prediction already makes. The cost is that a surface still growing, but more slowly each week, reads as silent at any ratio. That is accepted, because slowing growth is what convergence means here.

**Replayed 2026-11-03** over the store on this branch, calling `docket.inflow.missed` at the first day after each week from 2026-09-28 to 10-26 ended, with the old rule and the new. Every line is the same except one: the week of 2026-10-26 to 11-01 no longer reports its 11 new paths over 19 filings, because 11 is fewer than the 34 of the week before. Its `P1` line about `PL-D59R` still prints. The weeks from 2026-10-12 and 2026-10-19 still break the ceiling, with 30 against 6 and 34 against 30.
