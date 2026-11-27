---
id: PL-0DRD
title: RunFrame.agent_id and HoverReading.quantity in the chart frame are read only by tests
priority: P3
effort: S
status: ready
classes: refactor
feature: unit-test-review
touches: src/anesthesia_sim/app/chart_frame.py, tests/unit/test_chart_frame.py, tests/integration/simulation_view/test_simulation_view_run_values.py, tests/integration/simulation_view/test_simulation_view_held_window.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the release waits on the owner test drive and two live safety entries, so it is deferred rather than holding the release (triage 2026-11-27)
added: 2026-11-23
filed-pr: 2306
payoff: the chart frame carries only what the view draws, so its tests check what a learner sees
---

**Problem.** `RunFrame.agent_id` and `HoverReading.quantity` in `src/anesthesia_sim/app/chart_frame.py` are read by no code in `src/`. Tests read them: `frame.runs[0].agent_id` in `tests/integration/simulation_view/test_simulation_view_run_values.py` and `tests/integration/simulation_view/test_simulation_view_held_window.py`, and `reading.quantity` in `tests/unit/test_chart_frame.py`. A field kept only for a test makes the frame larger than what the view draws from it, and the test then checks a value no reader shows.

`PL-PZSF` found it on 2026-11-23 and kept both, since removing them needs the tests changed first.

`HoverReading.quantity`'s docstring says it is stored on each reading so that a hover never leaves the reader to infer which trace a value is on (`PL-0RZ0`). So before removing it, check how the hover box names each value's trace today, and whether that label should be read from this field.

**What to do.** Make each test check what a reader sees instead, such as the run's agent display name or the hover text, then remove the two fields. If a test needs a field to tell two runs or two quantities apart, keep that field and say why in a comment.

**Why it matters.** A field that only tests read lets those tests pass on a value that no reader sees, while what the view actually draws goes unchecked by them.

**Reproduced 2026-11-27.** On `main` at `f653c1eb`, no module under `src/` reads either field. The hover box names each value's trace from the compartment that `format_compared_trace_hover` receives with each point, not from `HoverReading.quantity`, so removing the field does not take the trace's name off the hover. The test paths above were corrected the same day: both integration tests now sit under `tests/integration/simulation_view/`.

**Done when.** Neither field is in `src/anesthesia_sim/app/chart_frame.py`, and each test that read one checks what a reader sees instead, such as the run's agent name or the hover text. Where a test needs a field to tell two runs or two quantities apart, that field stays, with a comment saying which test needs it.

**Generator check.** One-off. A field outlived its last reader, and `PL-PZSF` found it while sorting the mutation survivors of `PL-00Y5`. The fact it concerns is which fields the view draws from the frame, and no head states it.
