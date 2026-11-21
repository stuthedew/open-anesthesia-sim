---
id: PL-MH9J
title: Store every second's state of a run in one array, and have the chart, the readouts, the marks, the wash-in label and the export read that array
priority: P1
effort: L
status: done
classes: refactor, safety
feature: run-computed-one-way
touches: src/anesthesia_sim/core, src/anesthesia_sim/app, tests, docs/MODEL.md, docs/INTERFACE.md, docs/ARCHITECTURE.md, .claude/rules/run-is-its-definition.md
blocked-by: PL-SZ6G
deferred-from: v0.7.0 - filed 2026-11-21, after the gate froze, as the build of the design the owner chose in PL-7CY5; each of the four pull requests leaves main releasable, so the release does not wait for the feature to finish
added: 2026-11-21
closed: 2026-11-21
pr: 2180
tests: tests/integration/controller/test_controller_stored_states.py::test_a_branch_stores_its_parents_state_at_the_fork_and_steps_on_from_it
---

**Problem.** Store every second's state of a run in one array, and have the chart, the readouts, the marks, the wash-in label and the export read that array

**Why it matters.** Today a run's states are computed on demand by three routes: the stepped system, `RunDefinition.state_at` and the display's `evaluate` and `evaluate_anchored`. They agree only to rounding, so each comparison between them needs an allowance, and a MAC target once read as reached on the trunk and not on a branch opened at the same step (`PL-QVBR`). The owner chose this design on 2026-11-21 in `PL-7CY5` (one rule for computing a run), which holds the counts, the measurements and the sources. The four items of the feature `run-computed-one-way` are built in this order: `PL-SZ6G`, `PL-MH9J`, `PL-FST0`, `PL-Z6C8`.

**What it changes.** Each step appends its state to one array for the run, nine numbers per second for one agent, about 6.2 MB over 24 hours. The chart, the readouts, the marks and MAC targets, the wash-in label and the export read that array and nothing else. Nothing draws an interpolated value between two stored seconds, because that would be a second route to a displayed number. `.claude/rules/run-is-its-definition.md` is rewritten in the same pull request, because it forbids exactly this store.

**Done when.** Every displayed or exported state is read from the stored array, and a test shows that the chart, the readouts and the marks read the same stored state for each second.

**Generator check.** Work the owner asked for on 2026-11-21, building the design that `PL-7CY5` decided. It is not a head. The fact is `PL-GJ1W`'s, how far a computed value can be from the exact one: one stored state per second removes the second and third routes to a state that `PL-QVBR` and `PL-81Q2` came from.

**Built, 2026-11-21: what is stored, and who reads it.** `core/stored_states.py` holds the record, a `StoredStates`: one `array` of nine doubles per second, from the second the run opened at to the second it has reached. `SimulationState.advance()` appends the state that the step wrote and then moves the clock. If the record refuses the state, the step is undone. The clock and the record cannot be written apart: the state refuses a count that the record does not reach, and refuses a replacement record. In `app/controller.py`, the readouts (`snapshot()`), the chart's drawn window (`drawn_window`), the test of a mark (`_step_ending_here`) and the opening of a branch (`_open_at`) read the record. The wash-in plot reads the same drawn window as the chart. The app has no export yet, so no export code changed.

**The stored state is the state the step wrote.** It holds each fraction as the step wrote it to its compartment, the case's delivered and exhausted totals, and the constant one. It is not read back from the compartments, because a compartment holds an amount and returns the fraction as amount over capacity. Measured on 2026-11-21 over 3,600 steps of the default patient, a fraction read back differed in the last bit from the fraction written in 2,946 of 21,600 readings for sevoflurane, 2,706 for isoflurane and 1,903 for desflurane, by at most 2.2e-16 of the value. A branch restores its parent's stored state with `resume_at`, which makes the same writes as the parent's step did. So the branch's compartments hold the same amounts as the parent's, and its later fractions repeat the parent's bit for bit where no setting moves (`test_a_branch_stores_its_parents_state_at_the_fork_and_steps_on_from_it`). The script is `release-trajectory/stored_states_readback.py` in the project's shared folder.

**The chart and the readout disagreed before this change, at 148 of 150 seconds.** A variant of the new test that needs no stored states compares the chart's newest point with the readout of the same second, over a 150 s sevoflurane run with setting changes at 40, 95 and 120 s. Run on the tree at `84bf3e7bc`, before this change, with `PYTHONPATH=<that tree>/src python stored_states_chart_against_readout.py`, it printed "seconds where the chart's newest point differs from the readout: 148 of 150; values: 880 of 900; first: (3, ('inspired_partial_pressure_fraction', 0.0006452066393084063, 0.000645206639308407))". On this branch it prints 0 of 150 and 0 of 900. The script is in the same shared folder.

**The chart draws the same seconds as before.** `drawn_seconds` (`app/chart_time_base.py`) returns both ends of the window moved inward to whole seconds, each multiple of the column spacing counted from the case's zero, and each second at which a setting changed. Only where their states come from changed. Drawing each column's lowest and highest stored values is `PL-BLZJ` (a swing shorter than one column), which holds one measured case: a peak drawn 0.05 percentage points low.

**The preview still computes by formula.** `preview_window` shows the run past the second it has reached, so the record holds no state for it. It opens a prediction from the stored state at the reach and evaluates it with `RunDefinition.evaluate_anchored`. The preview fills half the window (`app/chart_time_base.py`'s `preview_window`), so a stepped preview on the twelve-hour window would take 21,600 steps for each frame, about a second at the step cost below. `PL-Z6C8` decides what replaces it, and must measure that cost first.

**One test was deleted.** `test_a_step_whose_two_readings_straddle_a_band_edge_halts_where_a_branch_does` (`tests/unit/test_bookmarks.py`) built a step whose live reading and evaluated reading lay on either side of a band edge. A step now has one reading for each end, so the case cannot be built. Three tests beside it were restated on stored states.

**Left for `PL-FST0` (branch at any whole second).** A branch's delivered and exhausted totals can differ from its parent's in the last bit after the fork. The uptake system adds each step's delivered and exhausted agent with a compensated sum, and the stored state holds the totals without the sum's correction term, so a branch restarts the sum without it. Observed: 0.8552814829837884 against 0.8552814829837883 L exhausted. The test of a branch therefore holds the two totals to eight times the spacing of doubles and the six fractions exactly. `_keyframe_before` returns the branch's `stepped_from` keyframe for a step that began before the fork, which `PL-FST0` removes when a branch copies its parent's record.

**Left for `PL-Z6C8` (remove the old evaluation paths).** `BookmarkSet.needs_canonical_readings`, `_near_band_edge` and `LIVE_READING_GAP` in `app/bookmarks.py` have no caller in `src/`. Some controller tests still compare two runs through `RunDefinition.state_at`, and `CLOSED_FORM_AGREEMENT` in `tests/integration/controller/test_controller_run_definition.py` is unused. The rule file keeps the name `run-is-its-definition.md`, which no longer describes it: `core/run_definition.py` cites it by that name.

**Costs, measured 2026-11-21 in this session's container.** Checking a state before it is stored took about 5 µs. A step with the store took 37 to 57 µs, the higher figure while the test suite was running beside it. A 24-hour run's record is 86,401 states, about 6.2 MB.

**The code's prose was reworded, 2026-11-21.** The docstrings and comments in `app/` and `core/` that described readings computed from the run's settings now describe the stored states. With docstrings removed, each edited file's syntax tree equals its tree before the rewording. Three refusal messages that named `RunDefinition.state_at` or the recorded settings as the source of a state now name the stored states.

**More left for `PL-Z6C8`, found during the rewording.**

1. `require_canonical_state`'s docstring in `core/governing_equations.py` still describes two paths to a state.
2. `preview_window` builds a new `RunDefinition` for each frame, so the propagators that one frame forms are not kept for the next.
3. A branch's run definition holds a keyframe at the fork that is computed by formula. Nothing shows it, but `run_segments` returns it.
4. `SimulationController.bookmark_standings`' docstring says that none of its inputs builds a `Fraction`, and `_crossings_stood_on` builds them.
5. `app/run_view.py`, `app/run_presentation.py` and `app/theme.py` mention refusals from `snapshot()` and were not checked.
6. These figures in docstrings were measured on the earlier design and were left as they were: "6.9e-14 L" in `resume_at` (`core/uptake_system.py`); "about 70 KiB" against "3.16 GB", "6.2 us" and "1.29 ms" in `core/run_definition.py`; "up to 5.3e-13 in an accumulator" in `resumed_at`; "48 of 54 elements differ" in `resumed_here`; and "40 of 45 elements differed" and "11.7%" in `_open_at` (`app/controller.py`).

**Closed 2026-11-21.** The leftovers this brief handed to `PL-Z6C8` were removed there: `needs_canonical_readings`, the near-edge check and `LIVE_READING_GAP`. The preview now steps one second at a time (`core/prediction.py`).

**Documents checked, 2026-11-21, after `PL-Z6C8`.** `docs/INTERFACE.md` § "Halting on a marked crossing", § "A run stores the state of every second it reaches", § "Each second has one stored state", § "The shared history is identical by construction, not by measurement", § "What the chart draws" and § "A preview of an unapplied setting"; `docs/MODEL.md` § "The reproducibility guarantee", § "Supported simulation step", § "Supported input ranges", § "The numerical envelope", § "How far a computed value can be from the exact one", § "Step-refinement test", § "Prediction agreement test" and § "Stored-state test"; `docs/ARCHITECTURE.md`'s package map and its sections on the run record and on branching; `ROADMAP.md`'s item 12 entry; `.claude/rules/run-is-its-definition.md`. The remaining passages that `PL-5FMC` listed for this build are `PL-LZ54`'s.
