---
id: PL-G2WC
title: No test checks that a value shown in compare mode sits under its own run: the readout test checks the 'Run 1' and 'Run 2' labels and never a value against the run it names
status: untriaged
feature: every-view-in-run-state-tests
added: 2026-11-10
---

**Problem.** No test checks that a value shown in compare mode sits under its own run: the readout test checks the 'Run 1' and 'Run 2' labels and never a value against the run it names

**Checked 2026-11-10:** `PL-GTH6` (which run a displayed value belongs to once two runs are shown) closed on 2026-10-25 with `generator: spent - no member filed since 2026-09-21 across 34 days of compare-mode changes (inferred from the store)`. It names no check. `tests/integration/test_compartment_schematic_view.py` and `tests/integration/test_agent_cost_view.py` assert the run names "Run 1" and "Run 2". The audit's reviewer reported that no test compares a displayed value with the run it sits under, for any View. The filing session confirmed the two name assertions and did not read every compare-mode test, so confirm that first.

**Why it matters.** In compare mode a learner reads two runs side by side, and a value shown under the wrong run's name is a correct number in the wrong context. The record that this cannot happen is an absence of filings.

**Done when.** A test loads two runs that differ in agent and in settings, and for every View that shows two runs checks each displayed value against the value of the run it is shown under. The Views come from the registry, as in `PL-B8DL` (the test layout built from the registry), so a new View is included without being listed.

**Generator check.** An instance of `PL-GTH6`'s fact, filed after that head closed on 2026-10-25. The head's verdict rests on no filing having arrived, not on a check.
