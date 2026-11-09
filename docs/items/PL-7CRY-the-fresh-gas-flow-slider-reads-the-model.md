---
id: PL-7CRY
title: The fresh gas flow slider reads the model envelope alone, so a machine profile declaring a narrower deliverable range would offer settings the circuit refuses
priority: P3
effort: S
status: done
classes: anticipated, defect
feature: anesthesia-machine
milestone: v0.5.24
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "Nothing misleads anybody in the meantime".

> **One more from closing `PL-8PS6`** (`PL-7CRY`, 2026-09-20). That work split the model's fresh gas flow envelope from a machine's deliverable range. It left the interface reading the envelope alone, so a profile that declares a narrower range would offer settings that the circuit refuses. `PL-7CRY` applies to `src/anesthesia_sim/app/`, so it could affect a reader of the simulator, which rules out the refilling-queue ground. It is declined on the ground on which `PL-5B1N` and `PL-QYBW` are recorded: **nothing is misleading anybody meanwhile.** No shipped machine profile declares a range. None could be obtained for any machine that the 2026-09-19 survey covered. So the intersection *is* the envelope today, and the slider's bounds are correct. The refusal it would prevent is itself correct, and that refusal names which of the two claims was violated. So what the item buys is an error prevented rather than an error corrected. That is `.claude/rules/expert-review.md`'s preference, not a live defect. It becomes live with the first profile that declares a range. That profile is the work of planned-milestone item 1, not of this gate.

> - PL-7CRY (S) The fresh gas flow slider reads the model envelope alone, so a machine profile declaring a narrower deliverable range would offer settings the circuit refuses
