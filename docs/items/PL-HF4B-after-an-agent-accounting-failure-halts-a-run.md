---
id: PL-HF4B
title: After an agent-accounting failure halts a run, the rollback restores the previous step's passing validator, so the accounting panel reads "Valid" and "The simulation still accounts for all delivered agent" directly under a banner saying accounting validation failed, and the banner quotes the failed step's delivered and stored totals beside the panel's different restored ones
priority: P2
effort: S
status: ready
classes: defect, ux
feature: replay-findings
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/agent_simulation_validation.py, src/anesthesia_sim/core/exceptions.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, tests/unit/test_dashboard_frame.py, tests/integration/test_controller.py, tests/integration/test_simulation_view.py
added: 2026-10-25
payoff: the accounting panel reports a conservation failure at the moment one is detected, instead of saying Valid under the banner that reports it
verify: grep -q 'def test_the_accounting_panel_reports_the_failure_after_an_accounting_halt' tests/unit/test_dashboard_frame.py
reenters: PL-X7D5
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

**Design, 2026-10-26 (session on `claude/generator-head-state-consistency-o6wts7`, under the head `PL-J5GC`).** The head's rule settles which totals the panel shows. A verdict must come from the same step as the totals it judges. So "Validation failed" beside the restored totals would only move the two-state defect inside the panel. After an accounting halt, the panel's verdict, detail and amounts all describe the rejected step, and the detail line says so: that step was rejected and rolled back, and these are its totals. The fact is recorded where it is known, not parsed back out of the failure string:

1. `AgentSimulationValidationError` carries the failing `AgentSimulationValidationResult`, which `require_valid_agent_accounting` already builds as `check`.
2. `RunView.halt` passes that check to `SimulationController.fail`. `RunStatus` gains a field holding it, `None` for every other run, and `reset()` and `set_agent()` clear it as they clear `failure_reason`.
3. `dashboard_frame.accounting` reads the panel from that check where one is set, and from the snapshot's accounting fields otherwise.
4. The validator's message labels its totals as the rejected step's. The banner quotes the message, so its totals are labelled too.

`core/agent_simulation_validation.py`, `core/exceptions.py` and `tests/integration/test_simulation_view.py` join `touches`. One point is left to settle while building. `FAILURE_NOTICE_TEMPLATE` says "The values shown are the last completed step", and the panel now shows the rejected step's totals under its own label. Either the panel's label is enough, or the banner's sentence excepts the panel. That is a wording choice, so the building session decides it and records it here as a placeholder.

**Built, 2026-10-26 (`c2f66e41`).** As designed above. `AgentSimulationValidationError` takes `check` as an optional keyword argument, and `require_valid_agent_accounting` passes it. Its message now reads "Agent accounting validation failed, so the step was rejected and rolled back. The rejected step's totals: …". `RunStatus.rejected_accounting` is keyword-only with no default. `SimulationController.fail` takes it as an optional keyword argument, keeps it only with the first failure, and `_build_state` and `reset()` clear it. `RunView.halt` passes `error.check` for an `AgentSimulationValidationError`. `accounting()` shows the rejected check's verdict and amounts through a new `_accounting_amounts`. The wording point is decided as a placeholder: the panel's label alone would leave the banner's "The values shown are the last completed step" false for the panel. So `notice` words such a failure with `REJECTED_ACCOUNTING_NOTICE_TEMPLATE`, which adds "except the agent accounting panel, which shows the rejected step". The detail line is `ACCOUNTING_REJECTED_DETAIL_TEXT`: "A step failed this check and was rolled back. The amounts below are that step's." `test_the_accounting_panel_reports_the_failure_after_an_accounting_halt` needs the interface the fix added, so its rule 6 variant is `PL-J5GC`'s accounting-halt scenario, which fails on `main` at `e042ab8c` with `'verdict': 'Valid'`. Still to do: `docs/MODEL.md`, under `PL-J5GC`'s close-out.

