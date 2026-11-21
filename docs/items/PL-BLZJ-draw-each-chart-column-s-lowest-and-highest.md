---
id: PL-BLZJ
title: Draw each chart column's lowest and highest stored value where a window holds more seconds than columns, so a swing shorter than one column is not left out
priority: P1
effort: M
status: done
classes: feature, safety
feature: run-computed-one-way
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/chart_frame.py, docs/INTERFACE.md
added: 2026-11-21
closed: 2026-11-21
pr: 2180
tests: tests/unit/test_chart_frame.py::test_a_preview_after_turning_the_dial_off_draws_each_peak_the_run_would_reach
---

**Problem.** Where a chart window holds more seconds than columns, the chart draws one stored state per column, at multiples of the column spacing counted from the case's zero. It also draws both ends of the window and each second at which a setting changed (`app/chart_time_base.py`'s `drawn_seconds`, read by `SimulationController.drawn_window`). A compartment can turn between two drawn seconds. After a short overpressure, the alveolar concentration peaks some seconds after the dial is lowered. The lowering is drawn, and the peak is drawn only if it falls on a column. Measured on 2026-11-21 with the default sevoflurane patient, the dial at 8% for 120 s and then at 1%: the alveolar fraction is 2.427% at 120 s, peaks at 2.480% at 128 s and is 2.378% at 144 s. A window whose columns are 144 s apart draws 120 s and 144 s, so its highest drawn value is 0.05 percentage points below the peak.

**Why it matters.** A learner reading the chart for the highest alveolar concentration that an overpressure reached can read a value below the true peak. The readouts are not affected: they show the stored state of the second the run stands on.

**Measured on a 1,000 px plot, 2026-11-21.** `docs/INTERFACE.md` § "Interface boundary" said that a drawn line misses a peak by 0.0028 percentage points at most, under half the readout's resolution of 0.01 (`PL-GS3R`). At whole-second spacings (`PL-SZ6G`) the largest gap over the same five runs is 0.0094, on the mixed venous trace of the desflurane dial-down on the eight-hour time base. The gap depends on where the change falls between two columns, which those five runs do not vary: the same dial-down at the reference adult's flows, made at 629 s, leaves 0.036 on the vessel-rich trace on the twelve-hour time base. That is more than three times the readout's resolution, and it does not come from the step. The scripts are `release-trajectory/iface_extremum_gap.py` and `iface_extremum_phase.py` in the project's shared folder. `tests/unit/test_run_definition.py`'s `test_a_pixel_wide_chord_misses_an_extremum_by_under_the_readout_s_resolution` still passes because it draws at 43.2 s, a spacing the chart no longer uses. At 43 s the same run gives 0.0065, above its limit of 0.005.

**What it changes.** Since `PL-MH9J` every second of a run has a stored state (`core/stored_states.py`), so a column's lowest and highest values can be read from the record without computing anything. The established method is M4, which draws each column's first, last, lowest and highest values: Jugel U, Jerzak Z, Hackenbroich G, Markl V. M4: A Visualization-Oriented Time Series Data Aggregation. Proc VLDB Endow. 2014;7(10):797-808. `PL-8LXM` (the item that deleted the chart's earlier M4 module) holds that implementation, the citation and an analysis of where it departed from the paper's Theorem 1. Start from that record.

**Found in.** `PL-MH9J` (store every second's state), 2026-11-21. That item kept the seconds the chart drew before it and changed only where their states come from.

**Generator check.** Found while building `PL-MH9J`, the work the owner asked for on 2026-11-21. It is not a head. The fact is `PL-GS3R`'s, how far a drawn line can sit from the stored value it stands for: the chart chose which seconds to draw by column spacing alone, so a turn between two drawn seconds could fall out of the line.

**Done when.** Either a measurement shows that no drawn curve misses a turn by more than the chart can show, or the chart draws each column's lowest and highest stored values and a test draws a peak that falls between two columns.

**Built, 2026-11-21, on the branch that builds `PL-MH9J`.** `SimulationController.drawn_window` now also draws the second at which each compartment is highest and lowest between two drawn seconds, where that value lies outside both. `chart_time_base.extreme_seconds` finds those seconds, and `StoredStates.fraction_series` reads the six fractions at every second of the window. So in each stretch between two columns, the highest and the lowest point drawn for a compartment equal its highest and lowest stored values. This keeps the lowest and highest of M4's four points per column. The first and last are the stretch's own ends, which the chart already drew. At most two seconds are added to a stretch for each compartment.

**The new tests fail on the tree before the change.** Run on `b4b08e532` with `PYTHONPATH=<that tree>/src python -m pytest tests/integration/controller/test_controller_stored_states.py`, `test_a_peak_between_two_chart_columns_is_drawn_at_its_stored_value` failed with "assert 128 in {0: (0.0, 0.0, ...", and `test_every_compartments_highest_and_lowest_value_in_each_column_is_drawn` failed with "AssertionError: (120, 1)", "assert 0.024273126247874196 == 0.024799019733263063". Both expected values come from a run stepped in `core/`.

**A frame costs more, measured 2026-11-21 while the test suite ran beside it.** One frame of a twelve-hour window in 1,001 columns took 10.3 ms against 1.1 ms before, and drew 1,014 points against 1,007. One frame of a one-hour window took 3.5 ms against 1.1 ms. The interface draws a frame every 100 ms. The script is `release-trajectory/chart_frame_cost.py` in the project's shared folder.

**Not covered.** The F_A/F_I plot's ratio can still turn between two drawn seconds: `PL-DN13`. The preview past the run's reach still draws one predicted state per column (`RunDefinition.evaluate_anchored`), and `tests/unit/test_run_definition.py` now pins its gap for one run at 0.0065 percentage points. `PL-Z6C8` (remove the old evaluation paths) decides how the preview is computed.

**The preview is covered since `PL-Z6C8`, 2026-11-21.** The preview now steps one second at a time (`core/prediction.py`) and is drawn with each peak and trough between two columns, as a run is. With sevoflurane at 2% for five minutes and the dial then turned off, a preview on a 30 s grid draws the alveolar peak at 302 s, the vessel-rich peak at 363 s and the venous peak at 379 s (`test_a_preview_after_turning_the_dial_off_draws_each_peak_the_run_would_reach`). The test fails on `59e586095`, where the preview was drawn only at the grid seconds.

**Documents checked, 2026-11-21, after `PL-Z6C8`.** `docs/INTERFACE.md` § "Halting on a marked crossing", § "A run stores the state of every second it reaches", § "Each second has one stored state", § "The shared history is identical by construction, not by measurement", § "What the chart draws" and § "A preview of an unapplied setting"; `docs/MODEL.md` § "The reproducibility guarantee", § "Supported simulation step", § "Supported input ranges", § "The numerical envelope", § "How far a computed value can be from the exact one", § "Step-refinement test", § "Prediction agreement test" and § "Stored-state test"; `docs/ARCHITECTURE.md`'s package map and its sections on the run record and on branching; `ROADMAP.md`'s item 12 entry; `.claude/rules/run-is-its-definition.md`. The remaining passages that `PL-5FMC` listed for this build are `PL-LZ54`'s.
