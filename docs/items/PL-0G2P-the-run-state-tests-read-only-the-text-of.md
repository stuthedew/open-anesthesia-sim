---
id: PL-0G2P
title: The run-state tests read only the text of labels, buttons, combo boxes and sliders, so a value that a View paints, as the compartment schematic paints its amounts, is in no restatement test
status: untriaged
feature: every-view-in-run-state-tests
added: 2026-11-10
---

**Problem.** The run-state tests read only the text of labels, buttons, combo boxes and sliders, so a value that a View paints, as the compartment schematic paints its amounts, is in no restatement test

**Checked 2026-11-10:** `_widget_state` in `tests/integration/test_simulation_view.py` records a widget's type, whether it is hidden or enabled, its style sheet, and the text of a `QLabel`, a button or a `QComboBox`. `src/anesthesia_sim/app/qt_schematic.py` draws its amounts with `painter.drawText`, so they are in no widget's text.

**Why it matters.** The run-state tests compare what `_widget_state` records before and after a change. A painted amount is not in that record, so a schematic that went on painting an earlier run's amounts would pass them. `PL-B8DL` puts the schematic into the layout these tests build; this item makes its painted text visible to them.

**Done when.** The schematic's paint code reads its strings from one function that returns the text it is about to paint. The run-state tests read that function for a painted View. A test fails when a painted string is left from an earlier run after a Reset, an agent change or a halt. Work it after `PL-B8DL`, the item that puts the schematic into the test layout.

**Generator check.** An instance of the fact `PL-X7D5` and `PL-J5GC` state (which widgets state a run's current state), filed after `PL-J5GC` closed on 2026-10-27: that head's guard reads widget text, and a painted value has none.
