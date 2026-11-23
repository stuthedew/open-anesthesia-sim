---
id: PL-0DRD
title: RunFrame.agent_id and HoverReading.quantity in the chart frame are read only by tests
status: untriaged
feature: unit-test-review
added: 2026-11-23
filed-pr: 2306
---

**Problem.** `RunFrame.agent_id` and `HoverReading.quantity` in `src/anesthesia_sim/app/chart_frame.py` are read by no code in `src/`. Tests read them: `frame.runs[0].agent_id` in `tests/integration/test_simulation_view_run_values.py` and `tests/integration/test_simulation_view_held_window.py`, and `reading.quantity` in `tests/unit/test_chart_frame.py`. A field kept only for a test makes the frame larger than what the view draws from it, and the test then checks a value no reader shows.

`PL-PZSF` found it on 2026-11-23 and kept both, since removing them needs the tests changed first.

`HoverReading.quantity`'s docstring says it is stored on each reading so that a hover never leaves the reader to infer which trace a value is on (`PL-0RZ0`). So before removing it, check how the hover box names each value's trace today, and whether that label should be read from this field.

**What to do.** Make each test check what a reader sees instead, such as the run's agent display name or the hover text, then remove the two fields. If a test needs a field to tell two runs or two quantities apart, keep that field and say why in a comment.
