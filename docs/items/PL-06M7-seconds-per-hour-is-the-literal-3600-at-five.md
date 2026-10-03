---
id: PL-06M7
title: Seconds per hour is the literal 3600 at five sites (core/supported_ranges.py:349, :393, :428; app/formatting.py:743, :800-803) while core/units.py names the minute and the hour's minutes; give it one home and read it there
status: done
feature: one-home-for-constants
touches: src/anesthesia_sim/core/units.py, src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/app/formatting.py, tests/unit
added: 2026-10-03
closed: 2026-10-03
verify: uv run pytest -q tests/unit/test_units.py tests/unit/test_supported_ranges.py tests/unit/test_formatting.py
---

**Problem.** Seconds per hour is the literal 3600 at five sites (core/supported_ranges.py:349, :393, :428; app/formatting.py:743, :800-803) while core/units.py names the minute and the hour's minutes; give it one home and read it there

**Why it matters.** Seven occurrences of the hour in seconds, typed by hand (the limit-in-hours messages of `require_supported_run_length`, `require_supported_step_count` and `require_supported_case_instant` in `core/supported_ranges.py`; `format_supported_run_length` and the three in `_duration_components` in `app/formatting.py`), three of them in the message that tells a learner the run has reached its supported length. `core/units.py` already names `SECONDS_PER_MINUTE` and `MINUTES_PER_HOUR` (PL-QRBB gave the minute one home); the hour's seconds has none, so the next formatting change types 3600 an eighth time. This is the first instance PL-40SJ's check would baseline, and clearing it first keeps that baseline honest.

**Shape.** `SECONDS_PER_HOUR: Final = SECONDS_PER_MINUTE * MINUTES_PER_HOUR` in `core/units.py`, with the docstring the module's other constants carry; the seven sites read it, and `_duration_components` in `app/formatting.py` reads `SECONDS_PER_MINUTE` for its `60.0` as well. No new behaviour; the existing formatter and supported-range tests cover every site.

**Done when.** `grep -rn 3600 src/anesthesia_sim` finds only comments, docstrings and two rungs of `TIME_BASE_LADDER` in `app/chart_time_base.py`, which are chart widths declared in seconds inside a module-level constant - the home PL-40SJ's rule asks for, not a unit conversion - and `tests/unit/test_units.py` pins `units.py`'s constants to their SI definitions and asserts the derivation. Corrected at pickup, 2026-10-03: the grep as first written also matched those two rungs, and no test file pinned `units.py`, so the work adds one.

**Generator check.** An instance of PL-40SJ, not a head.
