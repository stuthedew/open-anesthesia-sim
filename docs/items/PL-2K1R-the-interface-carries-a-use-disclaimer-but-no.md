---
id: PL-2K1R
title: The interface carries a use disclaimer but no interpretation one, so nothing tells a reader the compartment readouts and chart traces are modelled rather than measured
priority: P1
effort: S
status: done
classes: safety, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_view.py, tests/unit/test_dashboard_frame.py, tests/integration/test_simulation_view.py, docs/MODEL.md
added: 2026-09-13
closed: 2026-09-15
verify: uv run pytest tests/unit/test_dashboard_frame.py && grep -q 'def test_the_interface_says_the_readouts_are_model_outputs_not_measurements' tests/unit/test_dashboard_frame.py
---

**Problem.** The interface carries a use disclaimer but no interpretation one, so nothing tells a reader the compartment readouts and chart traces are modelled rather than measured

**Why it matters.** `docs/MODEL.md` states that no displayed value may be read
as accurate to its last digit as a prediction about a patient, and that sentence
lives only in a specification a learner will never open. The interface's own
standing notice is an *educational-use* disclaimer: it says what the tool is
*for*, not how to read a number on it. Those are different claims, and only the
second addresses this hazard.

The compartments this project exists to display - vessel-rich, muscle, fat,
mixed venous - are precisely the ones no monitor shows, so a reader has no
measured counterpart to check a trace against, and the polish of the display
argues the other way. `docs/MODEL.md` § "Reasonably foreseeable misuse, and the
hazards the presentation carries" carries this as the one row whose mitigation
is incomplete, and names this item as where the rest lives (`PL-FDBK`).

**The project owner has agreed the interface should carry an interpretation
statement distinct from the use disclaimer** (2026-09-13, answering `PL-FDBK`).
The wording and placement are open.

**The pattern to follow already exists in the codebase**, which is the reason
this is small. The control-input timeline labels its marks `"Settings only - not
a measurement."` at `src/anesthesia_sim/app/simulation_view.py`, held by
`test_the_interface_says_a_control_mark_is_an_input_not_a_measurement`. It works
because it is short, sits beside the thing it qualifies rather than in a banner,
and says what the value *is* instead of what the user must not do. `README.md`
carries the global form of the claim - "Every value on screen is a model output,
never a measurement" - which is the sentence to adapt.

**Where.** `src/anesthesia_sim/app/simulation_view.py` (the compartment readouts
and the chart), `tests/unit/test_simulation_view.py`, and `docs/MODEL.md` §
"Minimum displayed outputs" if the statement becomes required rather than
optional.

**Open questions for the owner**, both editorial: the exact wording, and whether
it sits once beside the readout block or is repeated on the chart. Worth noting
that repeating a disclaimer is how it stops being read, so once is the default
unless the chart is separable from the readouts in use.

**Done when.** The interface states, beside the modelled values themselves, that
they are model outputs rather than measurements; a test names the string; and
`docs/MODEL.md`'s hazard row is updated from "partially mitigated" to naming
that test.

**Triaged 2026-09-14: rides the Qt port** (project owner). `P1` because it is
the modelled-versus-measured line `CLAUDE.md`'s safety standard draws, on the
dashboard a clinician reads; `S` because it is text beside values that already
exist. Blocked on `PL-25KS` (port the dashboard) rather than built on Flet
first: the readouts and chart it sits beside are rewritten from scratch there,
so a Flet version is the same lines written twice - the port's own carried-fix
rule. It is named on `ROADMAP.md` § "v0.4.26 - the interface moves to Qt" →
"Decisions the port has to make anyway", which is what keeps the port's parity
claim - "identical except for this list" - checkable with this on it. It is
text the dashboard states, not a control a learner operates, so it is not new
capability by the `PL-16ZC` line.

**Closed 2026-09-15, with `PL-25KS`.** The interface states, on the readout
section's heading row beside "Modelled concentrations: {agent}", the line
`INTERPRETATION_DISCLAIMER_TEXT = "Model outputs — not measurements."` -
the timeline's pattern, short and beside the values it qualifies, saying
what they are. Once, not repeated on the chart, because the chart's hover
already names every value it reports as modelled and a repeated disclaimer
is one that stops being read. Held by
`test_the_interface_says_the_readouts_are_model_outputs_not_measurements`
(the string) and `test_the_readouts_say_they_are_model_outputs_beside_the_values`
(its placement inside the readout section), and `docs/MODEL.md`'s hazard row
now names both. The wording is the port's choice and the project owner may
revise it; drawn MUTED italic at the qualifier size, as standing text.
