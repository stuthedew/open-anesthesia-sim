---
id: PL-J791
title: Which readout panel is the clock is asked as 'quantity is None' in six places under app/, and the clock's playback line is built in three
priority: P2
effort: S
status: done
classes: defect
feature: one-source-of-truth
milestone: v0.6.20
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/run_presentation.py, tests/unit/test_dashboard_frame.py
deferred-from: v0.7.0 - captured after the freeze; every displayed value is correct, and one of the six copies came with PL-RF2S after it
added: 2026-11-11
closed: 2026-11-22
pr: 2225
payoff: adding or changing a readout panel cannot put the clock's playback line under the wrong panel
tests: tests/unit/test_dashboard_frame.py::test_no_module_under_app_asks_which_panel_is_the_clock_for_itself, tests/unit/test_dashboard_frame.py::test_only_the_first_panel_is_the_clock_and_the_rest_name_their_compartments, tests/unit/test_dashboard_frame.py::test_a_withheld_row_keeps_the_clock_s_playback_line
---

**Problem.** Which readout panel is the clock is asked as 'quantity is None' in six places under app/, and the clock's playback line is built in three

**What was found.** The readout row has one panel for the clock, and the code finds it by asking `panel.quantity is None`. That test is written in `app/dashboard_frame.py` (`readouts`, the panel's own row, and twice in `withheld_readouts`), `app/compartment_schematic.py`, `app/run_view.py` and `app/run_presentation.py`. Three of those places then build the clock's second line with `format_playback_rate`: `readouts`, `withheld_readouts` and `run_presentation._at_playback_rate`, which `PL-RF2S` added. The third adversarial review of `PL-RF2S` named the repeat on 2026-11-11.

**Why it matters.** A second panel with no quantity, or a clock that gains one, changes the answer at six places, and nothing fails at the one that is missed.

**Suggested fix.** Give the question one home in `app/dashboard_frame.py`, such as a field on the panel's definition or one function that returns the clock's panel, and one function for the clock's second line. Read both from the six places.

**Done when.** `quantity is None` is asked in one place under `src/anesthesia_sim/app/`, and the clock's playback line is built by one function.

**Reproduced 2026-11-11.** `grep -rn 'quantity is None' src/anesthesia_sim/app/` finds 7 lines, and `format_playback_rate(` is called on 5 lines outside its definition.

**Generator check.** A one-off, filed under the `one-source-of-truth` feature. No head's `misread:` states which readout panel is the clock. `PL-RF2S`, in flight on another branch, changes the same files, so this lands after it.

**Checked 2026-11-22** against `d4e8200`: still applies. `grep -rn 'quantity is None' src/anesthesia_sim/app/` still finds 7 lines: four in `dashboard_frame.py` and one each in `compartment_schematic.py`, `run_view.py` and `run_presentation.py`. `format_playback_rate` is still called in `dashboard_frame.py` (`readouts`, the width of the clock's second line, and `withheld_readouts`) and in `run_presentation.py`. `run_view.py` also calls it for the rate selector's entries, which is not the clock's line. The test the done condition names does not exist yet.

**Done 2026-11-22.** `ReadoutPanel` in `src/anesthesia_sim/app/dashboard_frame.py` now has `is_clock`, the one place that reads `quantity is None`, and `compartment()`, which returns the compartment or refuses the clock's panel. `COMPARTMENT_PANELS` lists the compartment panels in row order, and `clock_playback_line` builds the clock's second line. `readouts`, `withheld_readouts`, `READOUT_RESERVATIONS`, `WIDEST_READOUT_SECONDARY`, `run_presentation._at_playback_rate`, `run_view`'s clock index and widget map, and the five compartment loops in `compartment_schematic.py` read them. `run_view.py` still calls `format_playback_rate` for the rate selector's entries, which are not the clock's line. `test_no_module_under_app_asks_which_panel_is_the_clock_for_itself` scans `src/anesthesia_sim/app/`. It needs `COMPARTMENT_PANELS` to import, so the variant that ran against the code before the fix is the same scan as a script: it failed with `AssertionError: ['compartment_schematic.py', 'dashboard_frame.py', 'run_presentation.py', 'run_view.py']`. Files checked: `docs/INTERFACE.md` § "Minimum displayed outputs" and `docs/ARCHITECTURE.md` (neither names the predicate).
