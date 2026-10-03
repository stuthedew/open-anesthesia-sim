---
id: PL-06M7
title: Seconds per hour is the literal 3600 at five sites (core/supported_ranges.py:349, :393, :428; app/formatting.py:743, :800-803) while core/units.py names the minute and the hour's minutes; give it one home and read it there
status: untriaged
feature: one-home-for-constants
touches: src/anesthesia_sim/core/units.py, src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/app/formatting.py, tests/unit
added: 2026-10-03
---

**Problem.** Seconds per hour is the literal 3600 at five sites (core/supported_ranges.py:349, :393, :428; app/formatting.py:743, :800-803) while core/units.py names the minute and the hour's minutes; give it one home and read it there

**Why it matters.** Seven occurrences of the hour in seconds, typed by hand (`core/supported_ranges.py:349`, `:393`, `:428`; `app/formatting.py:743`, `:800`, `:801`, `:803`), three of them in the message that tells a learner the run has reached its supported length. `core/units.py` already names `SECONDS_PER_MINUTE` and `MINUTES_PER_HOUR` (PL-QRBB gave the minute one home); the hour's seconds has none, so the next formatting change types 3600 an eighth time. This is the first instance PL-40SJ's check would baseline, and clearing it first keeps that baseline honest.

**Shape.** `SECONDS_PER_HOUR: Final = SECONDS_PER_MINUTE * MINUTES_PER_HOUR` in `core/units.py`, with the docstring the module's other constants carry; the seven sites read it, and `_split_duration` at `app/formatting.py:800-803` reads `SECONDS_PER_MINUTE` for its `60.0` as well. No new behaviour; the existing formatter and supported-range tests cover every site.

**Done when.** `grep -rn 3600 src/anesthesia_sim` finds only comments and docstrings, and the test file that pins `units.py`'s constants asserts the derivation.

**Generator check.** An instance of PL-40SJ, not a head.
