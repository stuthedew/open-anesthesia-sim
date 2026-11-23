---
id: PL-72X2
title: The branch refusal for a rebuilt branch whose values disagree with its trunk shows code field names, raw float reprs and a docs path after 'Branch not opened —', and names no next step for a learner; word it for the learner and keep the field-by-field detail where a developer can read it
status: untriaged
feature: replay-findings
added: 2026-11-23
filed-pr: 2284
---

**Problem.** `SimulationController._branch_from` (`app/controller.py`) refuses a branch whose rebuilt values disagree with its trunk's. The branch panel shows the refusal after "Branch not opened —". It lists code field names with each value's `repr`, such as `agent_mac is 1.17 in this run and 1.1700000000000002 on the branch`, then a path into `docs/ARCHITECTURE.md`, and names nothing a learner can do. The `repr` is deliberate: two values that differ in the last bit must not print alike (`_disagreements_with`, `PL-NC62`). So the detail is right for a developer and wrong as the only text a learner sees.

**When it fires.** Only when a data file changed between the trunk's build and the branch's, so a learner meets it rarely. The `PL-3JTH` blind review (pass 1, F1, optional) found it.

**Done when.** The panel shows a learner sentence that says the run's agent or patient data no longer match and what to do, such as start a new case, and the field-by-field detail stays readable for a developer. `PL-XWCH` put a failure's technical detail behind "Show details"; read how it did that before choosing where this detail goes. A test drives the refusal through the branch panel.
