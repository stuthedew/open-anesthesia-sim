---
id: PL-ZZLW
title: Four tests call app/wash_in.py's read_wash_in, which skips the zero-ventilation rule, and describe its result as the plotted value; read_wash_in stays public, so a display caller can still bypass the rule
priority: P3
effort: S
status: done
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/app/wash_in.py, tests/reference/test_sevo_patient.py, tests/reference/test_published_wash_in_and_elimination.py, tests/integration/simulation_view/test_simulation_view_charts.py, tests/unit/test_dashboard_frame.py, tests/unit/test_wash_in.py
deferred-from: v0.7.0 - filed after the freeze; no displayed value is wrong, because every display path applies the zero-ventilation rule, so it does not hold the release
added: 2026-11-27
closed: 2026-11-28
pr: 2348
filed-pr: 2329
payoff: every test of the plotted F_A/F_I ratio reads it through the rule the display applies, so a display path that drew a ratio through an apnoea would fail a test
tests: tests/unit/test_wash_in.py::test_only_the_full_reader_calls_the_reader_without_ventilation, tests/unit/test_dashboard_frame.py::test_a_wash_in_state_with_undrawn_stretches_keeps_its_reading_before_the_count
---

**Problem.** Four tests call app/wash_in.py's read_wash_in, which skips the zero-ventilation rule, and describe its result as the plotted value; read_wash_in stays public, so a display caller can still bypass the rule

Found 2026-11-27 by the third adversarial review of `PL-49D5`'s change (#2329), which added rule 3 of `app/wash_in.py`: a state that a step at zero alveolar ventilation reached has no F_A/F_I ratio. `read_wash_in` applies rules 1 and 2 only, and `read_wash_in_with_ventilation` applies all three. Every display path in `src/` now calls the second.

1. Four tests still call `read_wash_in` and treat its result as the plotted value. `tests/reference/test_sevo_patient.py`'s `_plotted_wash_in_ratio` calls it "the one function that computes the plotted value". `tests/reference/test_published_wash_in_and_elimination.py` names its result `displayed`. `tests/integration/simulation_view/test_simulation_view_charts.py` and `tests/unit/test_dashboard_frame.py`'s `_reading` use it as the dashboard's reading. Every run those tests build is ventilated, so the values agree today, but none of them would notice a display path that dropped rule 3.
2. `read_wash_in` is still in `app/wash_in.py`'s `__all__`, and nothing stops a later display caller from calling it on a run's state.

**Done when.** Each of the four tests reads the plotted value through `read_wash_in_with_ventilation`, with the ventilation the run's step was taken at, or says that it tests rules 1 and 2 alone. `read_wash_in` is either private to `app/wash_in.py`, with `tests/unit/test_wash_in.py` testing rules 1 and 2 through the public reader, or its docstring and `__all__` entry say that it is not the plotted value.

**Why it matters.** A test that names a value "displayed" is where a later reader checks what the display does. Here it reads a value the display no longer computes, so it would pass beside a display that drew a ratio through an apnoea.

**Two files are reference tests.** Changing a line of a file under `tests/reference/` holds the pull request for the owner's read, so this goes in a pull request of its own rather than in #2329, which v0.7.0 waits on.

**Generator check.** One-off. It is the second reader of the ratio's domain that `PL-49D5` left behind when it added a rule, and every reader in `src/` was moved.


**Done, 2026-11-28.** The four tests now read the plotted value through `read_wash_in_with_ventilation`. `tests/unit/test_dashboard_frame.py`'s `_reading` and `tests/integration/simulation_view/test_simulation_view_charts.py` pass the snapshot's `reaching_alveolar_ventilation_l_min`. The two reference files keep their `read_wash_in` call and add an assertion that the full reader gives the same reading, with the ventilation the run was stepped at. `read_wash_in` stays public, and its docstring and `__all__` entry say that it is not the plotted value. A new test, `test_only_the_full_reader_calls_the_reader_without_ventilation`, parses every module under `src/` and fails if any function but `read_wash_in_with_ventilation` calls `read_wash_in`.

**Regression check.** With the call in `app/chart_frame.py`'s `_run_frame` changed by hand to `read_wash_in`, `uv run pytest -q tests/unit/test_wash_in.py -k only_the_full_reader` failed: `At index 0 diff: 'app/chart_frame.py::_run_frame' != 'app/wash_in.py::read_wash_in_with_ventilation'`. It passes on the current tree.

**Docs checked, 2026-11-28.** `docs/INTERFACE.md`, `docs/MODEL.md`, `docs/VERIFICATION.md`, `docs/PARAMETERS.md`, `docs/ARCHITECTURE.md` and `README.md` name no `read_wash_in`, so none changes. The `app/wash_in.py` module docstring's three rules are unchanged and still true.
