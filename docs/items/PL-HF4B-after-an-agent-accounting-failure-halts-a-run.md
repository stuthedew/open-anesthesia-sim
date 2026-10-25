---
id: PL-HF4B
title: After an agent-accounting failure halts a run, the rollback restores the previous step's passing validator, so the accounting panel reads "Valid" and "The simulation still accounts for all delivered agent" directly under a banner saying accounting validation failed, and the banner quotes the failed step's delivered and stored totals beside the panel's different restored ones
priority: P2
effort: S
status: ready
classes: defect, ux
feature: replay-findings
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/controller.py, tests/unit/test_dashboard_frame.py, tests/integration/test_controller.py
added: 2026-10-25
payoff: the accounting panel reports a conservation failure at the moment one is detected, instead of saying Valid under the banner that reports it
verify: grep -q 'def test_the_accounting_panel_reports_the_failure_after_an_accounting_halt' tests/unit/test_dashboard_frame.py
---

**Problem.** `AgentUptakeSystem.advance()` rolls back every failed step in its
`finally` clause, the validator included (`core/uptake_system.py`).
After an `AgentSimulationValidationError`, the snapshot therefore reports
`agent_accounting_passes_validation=True`. `accounting()` reads only that
flag (`app/dashboard_frame.py`). So the panel says "Valid" under a
banner that says accounting failed. The error message is not restated as
rolled back, unlike a `SimulationConfigurationError`. It still carries the
failed step's `delivered=` and `currently_stored=` totals
(`require_valid_agent_accounting` in `core/agent_simulation_validation.py`). Those differ from the
restored amounts the panel prints beside them.

**Why it matters.** The accounting panel is the one indicator built to show a
conservation failure. At the moment one is detected, it reports success, and
the same quantity appears twice with two values and no label saying which
step each belongs to. A fix could have the panel read the run's failure
reason, and mark the quoted totals as the rejected step's.

**Done when.** After an `AgentSimulationValidationError` halts a run, the accounting panel does not read "Valid", and any delivered and stored totals the banner quotes are labelled as the rejected step's. `tests/unit/test_dashboard_frame.py` has `test_the_accounting_panel_reports_the_failure_after_an_accounting_halt`, which builds the snapshot of a run halted that way and checks the panel's status and the banner's labels.

**Found by.** `PL-TBQS` reviewer replay on #204, findings r01 F3 (second
half), r02 F2, r03 F1, r04 F2, r05 F1 and r06 F2, and the `PL-ZWXD` entry
for #204. Checked against main on 2026-10-25. Reproduced by injecting a
failing `require_valid_agent_accounting` into a running controller after
10 s: the snapshot after `fail()` gave `passes_validation: True` and the
panel "Valid", under "Simulation stopped — AgentSimulationValidationError:
Agent accounting validation failed…" (scripts/a3_accounting_panel.py).
