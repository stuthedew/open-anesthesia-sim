---
id: PL-X4X2
title: The playback-rate line under the clock reads "300× real time" while the run is paused, reset or halted, but `docs/MODEL.md` § "Minimum displayed outputs" still defines that line as the rate at which simulated time is advancing, which contradicts § "Interface boundary"'s statement that the label states the setting
priority: P1
effort: S
status: ready
classes: docs, ux, safety
feature: replay-findings
touches: docs/MODEL.md, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_dashboard_frame.py
added: 2026-10-25
payoff: the specification gives one definition of the rate line under the clock, the one the screen matches, so a stopped run is not described as advancing
verify: ! grep -qF 'the rate at which simulated time is advancing' docs/MODEL.md && ! grep -qF 'State how fast simulated time is being played' src/anesthesia_sim/app/formatting.py
---

**Problem.** The clock panel's second line is built from the selected multiplier alone (`dashboard_frame.py`, `run_view.py`). So a paused, reset or halted run shows "300× real time" under a clock that is not moving. `docs/MODEL.md` § "Interface boundary" says the label states the setting. § "Minimum displayed outputs" still defines the required output as "the rate at which simulated time is advancing". `format_playback_rate`'s docstring (`formatting.py`) says the same.

**Why it matters.** One document gives two definitions of one required output, and the screen matches only one of them. A learner who glances at the clock panel of a stopped run is told it is running at 300×. The status word that corrects this sits in the transport row, not under the clock. A fix either rewords that entry and the docstring as the setting, or words the line by run state, for example "Paused · plays at 300×".

**Done when.** `docs/MODEL.md` § "Minimum displayed outputs" and the docstring of `format_playback_rate` define the line under the clock as the playback setting, as § "Interface boundary" does, and no longer as the rate at which simulated time is advancing. If the line is also worded by run state, `tests/unit/test_dashboard_frame.py` checks the wording for a paused run.

**Found by.** `PL-TBQS` reviewer replay on #331: r01 F2, r02 F3, r03 F4 and r06 F3, plus `PL-ZWXD`'s entry "the rate line still reads 300x while paused". Checked against main 2026-10-25 by reading the code. The halted-run case after a dropdown change was fixed separately by `PL-P58M`.
