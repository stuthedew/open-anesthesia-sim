---
id: PL-ZJRQ
title: PYTEST_BASELINE_S in tools/main_ci_status.py is the pytest step's time before PL-H9KW's fix (470 s), so once that fix lands it must be measured again over at least 100 successful main runs, or a suite that settles between 235 and 470 s leaves the drift line unable to catch a slowdown back up to 611 s
status: dropped
touches: tools/main_ci_status.py
blocked-by: PL-H9KW
added: 2026-10-17
closed: 2026-10-17
reason: Its premise was wrong. PL-H9KW's two changes that moved the test time, #1486 and #1487, merged on 2026-10-17 at 06:31 and 06:41 UTC, before PYTEST_BASELINE_S was measured, so no fix was still to land. The last 16 of the baseline's 100 runs came after #1487, and their pytest step's median was 502.5 s, 1.07 times the 470 s baseline, against 467.5 s for the 84 runs before. The step did not fall to about 300 s, which is the case this item was opened for, so there is nothing to measure again. The constant's comment in tools/main_ci_status.py now says when to measure it again: when a change moves the step's time on purpose.
---

**Problem.** PYTEST_BASELINE_S in tools/main_ci_status.py is the pytest step's time before PL-H9KW's fix (470 s), so once that fix lands it must be measured again over at least 100 successful main runs, or a suite that settles between 235 and 470 s leaves the drift line unable to catch a slowdown back up to 611 s

**Why it matters.** PL-YY32's line stays silent while the median of the last five runs is within 0.5 to 1.3 times `PYTEST_BASELINE_S`. If PL-H9KW's fix brings the step to about 300 s, the median sits at 0.64 times and the line stays silent, but the upper bound is still 611 s, twice the new time. A slowdown back to 600 s would then pass unseen, which is the October regression the line exists to catch.

**Done when.** `PYTEST_BASELINE_S` and its comment give the median over at least the 100 newest successful push runs after PL-H9KW's fix merged, measured as that comment says, or this item records that the fix did not move the time.

**Generator check.** Not a re-entry. This is the one follow-up that PL-YY32's baseline owes to a fix already in flight, and no other item reads the baseline.
