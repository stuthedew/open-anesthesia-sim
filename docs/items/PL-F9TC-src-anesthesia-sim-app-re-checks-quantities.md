---
id: PL-F9TC
title: src/anesthesia_sim/app/ re-checks quantities that core already owns: formatting.py checks mac_percent > 0 five times, playback.py checks tick_interval_s by hand instead of require_positive_finite, chart_time_base.py restates half the case-instant range twice, and simulation_view.py restates the 1-to-MAX_DISPLAYED_RUNS run count that RunCount holds
priority: P2
effort: M
status: ready
classes: refactor
feature: one-source-of-truth
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_formatting.py, tests/unit/test_playback.py, tests/unit/test_chart_time_base.py
added: 2026-10-19
payoff: the interface and core cannot disagree about which MAC, tick interval, case instant or run count a learner may set
verify: grep -q 'require_positive_finite' src/anesthesia_sim/app/playback.py && grep -q 'RunCount' src/anesthesia_sim/app/simulation_view.py
---

**Problem.** src/anesthesia_sim/app/ re-checks quantities that core already owns: formatting.py checks mac_percent > 0 five times, playback.py checks tick_interval_s by hand instead of require_positive_finite, chart_time_base.py restates half the case-instant range twice, and simulation_view.py restates the 1-to-MAX_DISPLAYED_RUNS run count that RunCount holds

**Why it matters.** Each of these is a rule that core already enforces once, written again in the interface. If core's rule changes, the interface's copy keeps the old one. The interface then refuses a value core accepts, or accepts one core refuses, and the two disagree about what a learner may set. `.claude/rules/expert-review.md` § "Parse, don't validate" asks for the check to be made once, by building a type, and for later code to take the type.

**Done when.** `formatting.py` takes a checked MAC type instead of testing `mac_percent > 0` five times. `playback.py` calls `require_positive_finite` for `tick_interval_s`. `chart_time_base.py` reads the case-instant range from its home. `simulation_view.py` takes a `RunCount` instead of comparing against `MAX_DISPLAYED_RUNS` itself. Each refusal the app makes today is still made, and a test proves it. `formatting.py` writes displayed clinical values, so the safety-critical standard applies to its part of the change.

**Checked 2026-10-24.** `formatting.py` has five `mac_percent` sign checks. `playback.py` does not call `require_positive_finite`. `simulation_view.py` compares `len(controllers) > MAX_DISPLAYED_RUNS` and does not use `RunCount`, which is defined in `chart_frame.py`.
