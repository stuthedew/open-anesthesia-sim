---
id: PL-B8DL
title: The four test layouts named _EVERY_VIEW hold four of the six registered Views, so the tests that every widget restates a run's state never build the compartment schematic or the agent cost View
priority: P1
effort: M
status: ready
classes: defect, safety
feature: every-view-in-run-state-tests
touches: tests/integration/simulation_view, tests/integration/test_qt_rendering.py, tests/integration/test_run_surfaces.py, tests/integration/test_view_contract.py
deferred-from: v0.7.0 - a new problem, not present at the freeze (817a4d88, 2026-10-25): the compartment schematic and the agent cost View merged on 2026-11-01 and 2026-11-02; not live: checked 2026-11-10, the audit's read of both Views found no value left from an earlier run, and the gap is in the tests
added: 2026-11-10
payoff: a value left over from an earlier run in the compartment schematic, the agent cost View or any later View fails a test, so a learner never reads one run's amount under another run's settings
verify: grep -q 'def test_the_shared_layout_holds_every_registered_view' tests/integration/test_view_contract.py
reenters: PL-J5GC
---

**Problem.** The four test layouts named _EVERY_VIEW hold four of the six registered Views, so the tests that every widget restates a run's state never build the compartment schematic or the agent cost View

**Checked 2026-11-10:** `src/anesthesia_sim/app/view_registry.py` defines six View kinds: `CONCENTRATION_CHART`, `WASH_IN`, `PARAMETER_CONTROLS`, `AGENT_ACCOUNTING`, `COMPARTMENT_SCHEMATIC` and `AGENT_COST`. Four test files each define a layout named `_EVERY_VIEW`: `tests/integration/simulation_view/`, `tests/integration/test_qt_rendering.py`, `tests/integration/test_run_surfaces.py` and `tests/integration/test_view_contract.py`. `grep -c COMPARTMENT_SCHEMATIC` and `grep -c AGENT_COST` print 0 for all four. The comment above the copy in `tests/integration/simulation_view/` says "One Workspace that holds every View this build registers". The schematic and the agent cost View merged on 2026-11-01 and 2026-11-02, after the layouts were written.

**Why it matters.** Three closed root causes rest on tests that walk the widgets of the layout they build: `PL-X7D5` (a widget keeps a value from an earlier run), `PL-J5GC` (a widget that states a run's state is not restated on some path) and `PL-5JTH` (a halt does not restate every panel). A View outside the layout is outside all three. The schematic and the cost View both show agent amounts, and each has one hand-written halt test of its own. The audit found no wrong value in either on 2026-11-10. The gap is that a value left over from an earlier run in one of them would fail no test, and neither would one in the next View anyone adds.

**Done when.** The four files import one layout that is built from the kinds the shipped registry holds. A test fails when a registered kind is missing from that layout. The run-state tests pass with the schematic and the cost View in the layout, and each failure they then show is fixed or filed.

**Generator check.** An instance of the fact `PL-X7D5` and `PL-J5GC` state (which widgets state a run's current state, and that each is restated on every path that changes it), filed after `PL-J5GC` closed on 2026-10-27. Those fixes compare every widget by default, but only inside a layout that is a list kept by hand. The audit of 2026-11-10 found the same shape in three other checks, and `PL-VZ57` lists them.
