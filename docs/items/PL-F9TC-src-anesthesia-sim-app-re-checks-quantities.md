---
id: PL-F9TC
title: src/anesthesia_sim/app/ re-checks quantities that core already owns: formatting.py checks mac_percent > 0 five times, playback.py checks tick_interval_s by hand instead of require_positive_finite, chart_time_base.py restates half the case-instant range twice, and simulation_view.py restates the 1-to-MAX_DISPLAYED_RUNS run count that RunCount holds
priority: P2
effort: M
status: done
classes: defect
feature: one-source-of-truth
touches: docs/ARCHITECTURE.md, docs/MODEL.md, src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/compartment_selection.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/uptake_system.py, tests/integration/test_controller.py, tests/integration/test_simulation_view.py, tests/unit/test_chart_frame.py, tests/unit/test_checked_number.py, tests/unit/test_compartment_selection.py, tests/unit/test_concentration.py, tests/unit/test_dashboard_frame.py, tests/unit/test_formatting.py, tests/unit/test_parameters.py, tests/unit/test_playback.py
added: 2026-10-19
closed: 2026-10-25
payoff: the interface and core cannot disagree about which MAC, tick interval, case instant or run count a learner may set
verify: grep -q 'require_positive_finite' src/anesthesia_sim/app/playback.py && grep -q 'displayed_run_count' src/anesthesia_sim/app/simulation_view.py && grep -q 'class MacPercent' src/anesthesia_sim/core/concentration.py
---

**Problem.** src/anesthesia_sim/app/ re-checks quantities that core already owns: formatting.py checks mac_percent > 0 five times, playback.py checks tick_interval_s by hand instead of require_positive_finite, chart_time_base.py restates half the case-instant range twice, and simulation_view.py restates the 1-to-MAX_DISPLAYED_RUNS run count that RunCount holds

**Why it matters.** Each of these is a rule that core already enforces once, written again in the interface. If core's rule changes, the interface's copy keeps the old one. The interface then refuses a value core accepts, or accepts one core refuses, and the two disagree about what a learner may set. `.claude/rules/expert-review.md` § "Parse, don't validate" asks for the check to be made once, by building a type, and for later code to take the type.

**Done when.** `formatting.py` takes a checked MAC type instead of testing `mac_percent > 0` five times. `playback.py` calls `require_positive_finite` for `tick_interval_s`. `chart_time_base.py` reads the case-instant range from its home. `simulation_view.py` takes a `RunCount` instead of comparing against `MAX_DISPLAYED_RUNS` itself. Each refusal the app makes today is still made, and a test proves it. `formatting.py` writes displayed clinical values, so the safety-critical standard applies to its part of the change.

**Checked 2026-10-24.** `formatting.py` has five `mac_percent` sign checks. `playback.py` does not call `require_positive_finite`. `simulation_view.py` compares `len(controllers) > MAX_DISPLAYED_RUNS` and does not use `RunCount`, which is defined in `chart_frame.py`.

**Built 2026-10-25.** Each check the interface restated now comes from the one rule that owns it.
- A MAC is a `MacPercent` (`core/concentration.py`), a `Percent` that refuses zero when it is built. The five formatters that divided by a MAC require that type instead of testing the sign themselves. A run opens with its dial built as a plain `Percent` setting, so a dial cannot be passed where the MAC belongs.
- `playback.py` checks the tick interval with `require_positive_finite`.
- `simulation_view.py` reads the number of displayed runs from `displayed_run_count`, which builds the `RunCount` type. `simulation_view.py` does not name the type itself, so the `verify:` line now looks for that function. It also checks that `MacPercent` exists.
- The chart's case-instant range had already moved to `require_case_instant` on main (`#1766`), so this branch kept main's version.
- `docs/MODEL.md` now says what the MAC check guarantees and what it leaves open. The type sets no lower bound beyond zero.
