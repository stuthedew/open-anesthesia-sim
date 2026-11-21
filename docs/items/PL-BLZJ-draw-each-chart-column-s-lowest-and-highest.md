---
id: PL-BLZJ
title: Draw each chart column's lowest and highest stored value where a window holds more seconds than columns, so a swing shorter than one column is not left out
status: untriaged
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/chart_frame.py, docs/INTERFACE.md
added: 2026-11-21
---

**Problem.** Where a chart window holds more seconds than columns, the chart draws one stored state per column, at multiples of the column spacing counted from the case's zero. It also draws both ends of the window and each second at which a setting changed (`app/chart_time_base.py`'s `drawn_seconds`, read by `SimulationController.drawn_window`). A compartment can turn between two drawn seconds. After a short overpressure, the alveolar concentration peaks some seconds after the dial is lowered. The lowering is drawn, and the peak is drawn only if it falls on a column. Measured on 2026-11-21 with the default sevoflurane patient, the dial at 8% for 120 s and then at 1%: the alveolar fraction is 2.427% at 120 s, peaks at 2.480% at 128 s and is 2.378% at 144 s. A window whose columns are 144 s apart draws 120 s and 144 s, so its highest drawn value is 0.05 percentage points below the peak.

**Why it matters.** A learner reading the chart for the highest alveolar concentration that an overpressure reached can read a value below the true peak. The readouts are not affected: they show the stored state of the second the run stands on.

**Measured on a 1,000 px plot, 2026-11-21.** `docs/INTERFACE.md` § "Interface boundary" said that a drawn line misses a peak by 0.0028 percentage points at most, under half the readout's resolution of 0.01 (`PL-GS3R`). At whole-second spacings (`PL-SZ6G`) the largest gap over the same five runs is 0.0094, on the mixed venous trace of the desflurane dial-down on the eight-hour time base. The gap depends on where the change falls between two columns, which those five runs do not vary: the same dial-down at the reference adult's flows, made at 629 s, leaves 0.036 on the vessel-rich trace on the twelve-hour time base. That is more than three times the readout's resolution, and it does not come from the step. The scripts are `release-trajectory/iface_extremum_gap.py` and `iface_extremum_phase.py` in the project's shared folder. `tests/unit/test_run_definition.py`'s `test_a_pixel_wide_chord_misses_an_extremum_by_under_the_readout_s_resolution` still passes because it draws at 43.2 s, a spacing the chart no longer uses. At 43 s the same run gives 0.0065, above its limit of 0.005.

**What it changes.** Since `PL-MH9J` every second of a run has a stored state (`core/stored_states.py`), so a column's lowest and highest values can be read from the record without computing anything. The established method is M4, which draws each column's first, last, lowest and highest values: Jugel U, Jerzak Z, Hackenbroich G, Markl V. M4: A Visualization-Oriented Time Series Data Aggregation. Proc VLDB Endow. 2014;7(10):797-808. `PL-8LXM` (the item that deleted the chart's earlier M4 module) holds that implementation, the citation and an analysis of where it departed from the paper's Theorem 1. Start from that record.

**Found in.** `PL-MH9J` (store every second's state), 2026-11-21. That item kept the seconds the chart drew before it and changed only where their states come from.

**Done when.** Either a measurement shows that no drawn curve misses a turn by more than the chart can show, or the chart draws each column's lowest and highest stored values and a test draws a peak that falls between two columns.
