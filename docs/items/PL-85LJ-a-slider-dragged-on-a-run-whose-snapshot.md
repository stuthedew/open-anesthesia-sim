---
id: PL-85LJ
title: A slider dragged on a run whose snapshot refuses leaves its value label on the previous value while the dial and the circuit hold the new one, because only refresh rewrites it and no frame draws after the halt (found at PL-V2HC's review)
priority: P1
effort: S
status: ready
classes: safety, defect
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_simulation_view.py
added: 2026-10-12
payoff: after a drag that halts the run, the number printed beside a dial is the value the dial and the run hold, not the one before the drag
verify: grep -q 'def test_a_drag_that_halts_the_run_leaves_its_label_on_the_dial' tests/integration/test_simulation_view.py
---

**Problem.** A slider dragged on a run whose snapshot refuses leaves its value label on the previous value while the dial and the circuit hold the new one, because only refresh rewrites it and no frame draws after the halt (found at PL-V2HC's review)

**Why it matters.** `_apply_setting` applies and records the setting, then
`_snapshot_for_a_control` halts the run (`PL-V2HC`) and no frame draws, so
`ParameterSlider.value_label`, written only by `refresh` through `set_setting`,
keeps the previous value beside a dial standing at the new one: dial at 4.0
L/min, label "2.0 L/min", circuit holding 4.0, until Reset. The halt banner
says the readouts show the last frame drawn, which covers the readouts and not
a label contradicting the reader's own gesture. Found 2026-10-12 by the
adversarial review of `PL-V2HC`; the same staleness held before it, with the
raise escaping the slot instead of the halt being stated.

**What a fix probably wants.** Rewrite the dial's own label from the setting
the controller holds when the gate halts the run - the settings are checked
types no snapshot is needed for - or lock the dials on a halted run, which
`PL-V2HC` recorded as the owner's call.

**Done when.** After a drag that halts the run, the label beside the dial reads
the value the dial and the run hold, shown by an integration test.
