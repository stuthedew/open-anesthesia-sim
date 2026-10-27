---
id: PL-M7K2
title: The four dial setters on SimulationController repeat the same five steps (refuse on a stopped run, read the old value, apply, record the change with an undo), so a fifth control has to copy all five by hand; one private method could hold them while each public setter keeps its own checked type
status: untriaged
feature: one-source-of-truth
added: 2026-10-27
---

**Problem.** The four dial setters on SimulationController repeat the same five steps (refuse on a stopped run, read the old value, apply, record the change with an undo), so a fifth control has to copy all five by hand; one private method could hold them while each public setter keeps its own checked type

**Evidence.** Found on 2026-10-27, when the owner asked on `#1846` why there are four dial setters. `set_fresh_gas_flow`, `set_delivered_concentration_percent`, `set_alveolar_ventilation` and `set_cardiac_output` in `src/anesthesia_sim/app/controller.py` each call `_refuse_a_setting_on_a_stopped_run`, read the value in force, apply the new one through the uptake system, and call `_record_control_change` with a `restore` that applies the old value again. Only the checked type, the `ControlInput` member and the part of the state each one writes differ. `PL-3B34` had to add its refusal to all four. Its test now runs once for each `ControlInput`, so a fifth control that leaves out the refusal fails it, but nothing makes the record or the undo appear in a fifth setter.

The four public setters should stay, because each takes the checked type that only its range check builds (`.claude/rules/core-domain.md`, parse, don't validate). What could be shared is the body. `PL-000W`, which is on `PL-ZR49`'s branch and not yet on `main`, maps each control to its settings field in two places. The same table could serve both items.

**Done when.** One private method in `controller.py` holds the refusal, the read, the apply and the record for every control, and each public setter is one call to it with its own checked type. Or the item records why the four bodies need to differ.
