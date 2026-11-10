---
id: PL-0G2P
title: The run-state tests read only the text of labels, buttons, combo boxes and sliders, so a value that a View paints, as the compartment schematic paints its amounts, is in no restatement test
priority: P1
effort: M
status: ready
classes: defect, safety
feature: every-view-in-run-state-tests
touches: tests/integration/test_simulation_view.py, src/anesthesia_sim/app/qt_schematic.py
deferred-from: v0.7.0 - a new problem, not present at the freeze (817a4d88, 2026-10-25): the compartment schematic, the first View that paints its values, merged on 2026-11-01; not live: checked 2026-11-10, the audit's read of the schematic found no painted amount left from an earlier run, and the gap is in the tests
added: 2026-11-10
payoff: an amount the schematic paints is read by the same tests as a label's text, so a painted amount left from an earlier run fails a test
verify: grep -q 'def test_painted_text_is_restated_when_the_run_changes' tests/integration/test_simulation_view.py
reenters: PL-J5GC
---

**Problem.** The run-state tests read only the text of labels, buttons, combo boxes and sliders, so a value that a View paints, as the compartment schematic paints its amounts, is in no restatement test

**Checked 2026-11-10:** `_widget_state` in `tests/integration/test_simulation_view.py` records a widget's type, whether it is hidden or enabled, its style sheet, and the text of a `QLabel`, a button or a `QComboBox`. `src/anesthesia_sim/app/qt_schematic.py` draws its amounts with `painter.drawText`, so they are in no widget's text.

**Why it matters.** The run-state tests compare what `_widget_state` records before and after a change. A painted amount is not in that record, so a schematic that went on painting an earlier run's amounts would pass them. `PL-B8DL` puts the schematic into the layout these tests build; this item makes its painted text visible to them.

**Done when.** The schematic's paint code reads its strings from one function that returns the text it is about to paint. The run-state tests read that function for a painted View. A test fails when a painted string is left from an earlier run after a Reset, an agent change or a halt. Work it after `PL-B8DL`, the item that puts the schematic into the test layout.

**Generator check.** An instance of the fact `PL-X7D5` and `PL-J5GC` state (which widgets state a run's current state), filed after `PL-J5GC` closed on 2026-10-27: that head's guard reads widget text, and a painted value has none.
