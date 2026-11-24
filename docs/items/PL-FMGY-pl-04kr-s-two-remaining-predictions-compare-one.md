---
id: PL-FMGY
title: PL-04KR's two remaining predictions compare one week's count with the week before, which counts this small break by chance; a trend test across the series is the established method
priority: P3
effort: S
status: done
classes: infra, planning
feature: convergence-visibility
touches: subprojects/docket/src/docket/inflow.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_inflow.py, subprojects/docket/README.md, docs/items/PL-04KR-pre-register-the-apparatus-convergence.md
deferred-from: v0.7.0 - filed after the gate froze; an apparatus reading with no effect on what a learner sees
added: 2026-11-23
closed: 2026-11-24
pr: 2316
filed-pr: 2301
payoff: a release cut reports a convergence miss only when the trend across weeks says so, not on one week's noise
tests: subprojects/docket/tests/test_inflow.py::test_the_laplace_statistic_matches_hand_worked_cases, subprojects/docket/tests/test_inflow.py::test_the_release_report_names_each_series_that_is_not_falling, subprojects/docket/tests/test_inflow.py::test_the_release_report_is_silent_when_both_series_fall
---

**Problem.** PL-04KR's two remaining predictions compare one week's count with the week before, which counts this small break by chance; a trend test across the series is the established method

**Found 2026-11-23**, answering the owner's request to research whether the convergence tracking is done correctly. `PL-04KR` pre-registered three predictions, and `PL-7TB2` retired the priority one. The two left each compare the last complete week with the week before it: new apparatus paths a filing, and re-entries. Weekly counts here are small. The week of 2026-11-16 held 30 ordinary filings and 0 re-entries (`PL-NJ54`), so one extra re-entry breaks the second prediction.

**Why it matters.** A comparison of two small counts breaks by chance, so each break costs a reading item that is likely to find nothing, as `PL-7TB2`'s six readings did. And a slow rise spread over several weeks may never break it.

**What the research says.**

1. Tsang (2012), a review of trend tests, West Indian Journal of Engineering 35(1):4-9 (https://www.sta.uwi.edu/eng/wije/vol3501_jul2012/documents/AReviewonTrendTests.pdf, read 2026-11-23): the Laplace trend test uses the whole series of failure times, and a test statistic below -1.96 shows reliability growth at the 5% level.
2. Mičko, Chren and Rossi, "Applicability of Software Reliability Growth Models to Open Source Software", arXiv:2205.02599 (full text read 2026-11-23): "perform a statistical test such as Laplace's trend test" to check for a decreasing failure trend before fitting a growth model, because without one "the SRGMs might not provide reasonable results".
3. Lakens (2024), Collabra: Psychology 10(1):117094, doi:10.1525/collabra.117094: a deviation from a preregistration needs a justification and an evaluation of its consequences. `PL-04KR` already records its deviations that way.

**Decision needed.** Should the release cut test whether apparatus inflow is falling across recent weeks, with the Laplace test, instead of comparing one week with the week before? The cut would then report a miss only when the trend is not downward at the 5% level.

**Recommendation.** Replace the two week-against-week predictions with the trend test. It answers the question `PL-04KR` was written to answer, whether inflow converges, and it does not break on one week's noise. It is the owner's call because it changes what `PL-04KR` committed to in advance.

**Done when.** The owner's answer is recorded here. If yes, `docket.inflow.missed` reports the trend test's statistic and verdict, a test pins it on a series with a known answer, `PL-04KR` records the deviation, and `subprojects/docket/README.md` describes the test.

**Generator check.** One instance, the same misreading `PL-7TB2` fixed for priority: a single week's count read as the trend.

**Answer, 2026-11-24.** Build the trend test (project owner, 2026-11-24, ratified, over keeping the week-against-week comparisons). The owner answered "Agree with best practice" to the recommendation above.

**Done 2026-11-24.** `docket.inflow.laplace` computes the statistic for observation that ends at a fixed time, from Tsang (2012), section 2.2(a): U = (sum(t_i) / T - n / 2) / sqrt(n / 12). Each event is placed at the midpoint of its day. `trend_test` applies it to the last eight complete weeks, counted from the first filing as the table's rows are, so the week still being filed into is left out. The two series are the days on which each apparatus path was first named, and the days of the re-entering filings that the `re-entry` column counts. `missed` reports a series whose statistic is not below -1.96, and `bin/docket inflow` prints both statistics under its table.

Three choices were made here rather than put to the owner, because each is internal and the research settles it or leaves it close:

1. Eight weeks. The window holds enough events to test, and leaves out the burst of filings in September 2026, when the apparatus was being built and a test over the whole history would read falling whatever happened since.
2. Ten events at least. Tsang gives no minimum for the Laplace test and treats the related Mann test as normal from ten events. A series with fewer than ten events in eight weeks is too quiet for its direction to change a decision.
3. Not falling is a miss, rather than significantly rising. `PL-04KR` predicted that inflow falls, and `CLAUDE.md` § "What this project is" says it should now decline, so a flat series breaks the prediction.

On the store of 2026-11-24 the window is 2026-09-28 to 11-22. New apparatus paths number 153 with a statistic of -0.68, so the next cut reports that prediction as broken. Re-entries number 83 with a statistic of -2.77, which is falling at the 5% level.

Files checked for prose the change made wrong: `subprojects/docket/README.md` (the inflow and release paragraphs, rewritten), `subprojects/docket/src/docket/inflow.py` (module docstring and `missed`), `subprojects/docket/src/docket/cli.py` (`_missed_expectations`), `subprojects/docket/src/docket/render.py` (`format_inflow`), `.claude/skills/docket/modes/release.md`, `.claude/skills/docket/modes/triage.md`, `CLAUDE.md` and `docs/items/PL-04KR-pre-register-the-apparatus-convergence.md`.
