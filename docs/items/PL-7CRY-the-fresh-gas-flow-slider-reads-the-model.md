---
id: PL-7CRY
title: The fresh gas flow slider reads the model envelope alone, so a machine profile declaring a narrower deliverable range would offer settings the circuit refuses
priority: P3
effort: S
status: done
classes: anticipated, defect
feature: anesthesia-machine
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, docs/MODEL.md, tests/unit
added: 2026-09-20
closed: 2026-10-12
pr: 1442
payoff: stops the fresh gas flow slider offering settings the mounted machine cannot deliver, once any profile declares a deliverable range - an error the control can prevent rather than warn about
verify: grep -q 'def test_the_fresh_gas_flow_control_narrows_to_a_declared_machine_range' tests/unit/test_dashboard_frame.py
recurrences: 2026-10-12 PL-1KQ9 withdrawn 2026-10-12 PL-1KQ9
---

**Problem.** The fresh gas flow slider reads the model envelope alone, so a machine profile declaring a narrower deliverable range would offer settings the circuit refuses

`PL-8PS6` split the two claims on the fresh gas flow: `core/supported_ranges.py`
declares the model's envelope, and a machine profile declares what that machine
can physically deliver in `deliverable_fresh_gas_flow_range`. The circuit
enforces the intersection. The interface does not: `app/dashboard_frame.py`
imports `MINIMUM_FRESH_GAS_FLOW_L_MIN` and `MAXIMUM_FRESH_GAS_FLOW_L_MIN`
directly for the slider's bounds, so the control offers the envelope whatever
machine is mounted.

**Why it matters.** `.claude/rules/expert-review.md` prefers an interface that
*prevents* an error to one that warns after it: a slider offering 0.2 L/min on a
machine floored at 0.5 L/min invites a refusal the control could have made
unreachable. The refusal itself is correct and says which claim it violated, so
nothing displayed is wrong - what is wrong is that the reader had to discover a
machine limit by hitting it.

**Not live, and the reason it is not.** Every shipped profile declares
`deliverable_fresh_gas_flow_range: null` - no operator's manual or manufacturer
specification giving a deliverable range was reachable for any surveyed machine
(`docs/machine-survey.md` § "(b8) Flow bounds, minimum oxygen flow, and the
hypoxic guard") - so the intersection *is* the envelope today and the slider is
correct. It becomes live with the first profile that declares a range.

**Where.** `app/dashboard_frame.py`'s fresh gas flow control descriptor, which
names the two constants; `core/circuit.py`'s `BreathingCircuit`, which holds
both claims and is the only object that can state the intersection;
`tests/unit/test_dashboard_frame.py`, which pins the slider's bounds to the same
two constants.

**A design question the work has to answer first.** The intersection is not
currently exposed - `BreathingCircuit` enforces it through two guards rather
than computing a range, deliberately, because each guard owes a different
refusal message and neither reads a merged pair. So this item either adds a
read-only property stating the effective range, or the controller composes it.
The first keeps one statement of the rule and is the recommendation; the second
puts a second copy of the intersection in `app/`, which is what
`PL-8PS6` argues against for the constants.

**Done when.** The fresh gas flow control's bounds are the intersection of the
model's envelope and the mounted machine's declared range, with a single
statement of that intersection rather than one per layer, and a test that a
profile declaring a narrower range narrows the control.

**Related.** `PL-8PS6` (the split this follows from, closed 2026-09-20),
`PL-WZVZ` (make an inter-machine difference attributable, the display half of
the machine abstraction), `PL-FG9D` (the machine abstraction itself).

**Built, 2026-10-12.** The recommendation above:
`BreathingCircuit.accepted_fresh_gas_flow_range_l_min` is the one statement of
the intersection, and `_require_the_two_flow_claims_overlap` now tests that
property for emptiness rather than restating the rule. The controller copies
it onto `SimulationSnapshot.accepted_fresh_gas_flow_range_l_min`, as
`max_delivered_concentration_percent` travels beside the vaporizer dial, and
`setting_readouts` bounds the control by it, so `app/` composes nothing.
`ParameterControl` lost its `minimum` and `maximum` fields, because two of the
four ranges are now the run's rather than constants. One thing the brief did
not anticipate: the slider steps at 0.1 L/min, so a declared end between two
steps, a floor of 0.25 L/min, would have been offered as the nearest step,
0.2 L/min, which the machine refuses. `offered_range` takes the step just
inside each end instead, and a range holding no step raises rather than
drawing a control whose only setting the run refuses. `app/controller.py`
joins `touches` for the snapshot field, and `docs/MODEL.md` for the paragraph
that said the control still read the envelope. Found and not fixed: a
profile's opening flow off the same grid (`PL-1KQ9`).
