---
id: PL-71CF
title: The fresh-gas-flow control is labelled as a flowmeter is, but the model reads it as common-gas-outlet flow, which is up to 22% higher
priority: P1
effort: S
status: done
classes: safety, ux
feature: presentation-safety
milestone: v0.4.10
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, docs/MODEL.md, tools/contrast_check.py
added: 2026-09-07
closed: 2026-09-08
pr: 462
verify: uv run pytest -q tests/unit/test_simulation_view.py && grep -q 'def test_the_fresh_gas_flow_control_names_the_common_gas_outlet' tests/unit/test_simulation_view.py
---

**Problem.** The fresh-gas-flow control is labelled as a flowmeter is, but the model reads it as common-gas-outlet flow, which is up to 22% higher.

`_build_parameter_controls` in `src/anesthesia_sim/app/simulation_view.py`
titles the panel `"Fresh gas flow"`, with a `format_flow` readout beside it and
no tooltip or qualifier. That is exactly the phrase on an anesthesia machine's
flowmeter bank, so a user maps the slider onto the flowmeters; `docs/MODEL.md`
§ "Breathing circuit" now states that the model's $`\dot V_F`$ is the flow at
the common gas outlet, carrier gas plus the vapour the vaporizer added. The two
differ by 1/(1 − F_D): negligible at ordinary dial settings, 22% at
desflurane's 18% Tec 6 maximum, where flowmeters at 2 L/min leave the common
gas outlet at about 2.44 L/min. The user-visible consequence is the circuit
time constant `V_C/V̇_F`, which is what the wash-in curve is about.

Found while working `PL-CXYT` (say what fresh gas flow counts in
`docs/MODEL.md`), whose `touches` did not reach the app; its "Done when"
required the interface label to be *checked* against the new sentence, which is
what produced this item. The document and the `BreathingCircuit` docstring now
carry the definition, so nothing is silently wrong — the gap is that the one
place a user actually reads is the one place that does not say it.

**Why it matters.** The error is a wrong clinical inference from a correct
number, which `CLAUDE.md`'s safety-critical standard counts as a presentation
failure rather than a wording preference: nothing the model computes is wrong,
and a user who reads the slider as a flowmeter still mis-sizes the wash-in they
are watching. It lands on the one control a user most readily maps onto a real
machine, and on the one agent this project ships whose dial reaches far enough
for it to matter.

**Decision, taken 2026-09-08.** Three options were put to the project owner:
qualify the label, tooltip it, or leave it and explain elsewhere. A longer
single-line label ("Fresh gas flow (common gas outlet)") costs width on a panel
that is a quarter of the row and would wrap where its three neighbours do not;
a tooltip is cheaper but is not reliably reachable by touch or keyboard in
Flet, and an explanation only some users see is weak for a safety-relevant
definition. The owner took the recommendation to **qualify the label**.

The form is the one this interface already has for exactly this problem:
`_build_metric_panel` draws a compartment name over a smaller italic gloss —
"Alveolar" over "end-tidal-equivalent" — because two lines at two sizes say
which claim is the weaker one where a single joined line offers them as
alternative names for one quantity (`PL-NV9W`). "Fresh gas flow" over "common
gas outlet" is the same move on a control instead of a readout, so a reader
meets one idiom rather than two.

**Done when.** The fresh-gas-flow panel draws "common gas outlet" under its
name, smaller and subordinate; no other setting panel draws a gloss, since a
gloss on a name that needs none is itself a wrong claim; a test holds both
strings and that pairing against the slider they belong to; `docs/MODEL.md`
§ "Breathing circuit" records the label as a requirement, so a later layout
pass cannot shorten it back; and the new `MUTED` instance is named in
`tools/contrast_check.py`'s declaration of that pair.
