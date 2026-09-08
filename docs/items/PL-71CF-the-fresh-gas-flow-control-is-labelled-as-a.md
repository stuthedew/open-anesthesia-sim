---
id: PL-71CF
title: The fresh-gas-flow control is labelled as a flowmeter is, but the model reads it as common-gas-outlet flow, which is up to 22% higher
status: untriaged
feature: model-spec-accuracy
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-09-07
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

**Decision, not a rename.** What the control should say is a presentation
judgment rather than a defect with one right answer: a longer label
("Fresh gas flow (common gas outlet)") costs width on a panel that is already
tight and uses a term a trainee may not know; a tooltip is cheaper but is not
reliably reachable on touch or by keyboard in Flet, and an explanation only
some users see is weak for a safety-relevant definition; and leaving the label
alone while explaining it in the run's own documentation is a defensible third
option, given the difference is under 9% for every agent but desflurane. Worth
deciding alongside `PL-5K5C` (record the vaporizer-class dependence of the
delivered-concentration dial), which raises the same question one control over.
