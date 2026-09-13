---
id: PL-74R0
title: core/ still holds four compartment-level advance methods that the coupled step no longer calls
priority: P2
effort: M
status: done
classes: defect, refactor
feature: numerical-domain
milestone: v0.4.17
touches: src/anesthesia_sim/core/__init__.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/patient.py, tests/unit/test_compartment_primitives.py, tests/unit/test_patient.py, tests/reference/test_sevo_patient.py
added: 2026-09-06
closed: 2026-09-13
pr: 516
verify: uv run pytest tests/unit/test_compartment_primitives.py tests/unit/test_patient.py -q
---

**Problem.** `PL-GS5X` replaced the five composed sub-steps with one exact
propagation, and `PL-LKRP` closed with it by deleting
`AlveolarCompartment.apply_blood_uptake`, whose only production caller was the
fifth of them. Four more mutators are in the same position and were left:

| Method | Production callers after `PL-GS5X` |
| --- | --- |
| `BreathingCircuit.advance_fresh_gas` | `BreathingCircuit.advance` and nothing else |
| `BreathingCircuit.advance` | none |
| `TissueGroup.advance` | `PatientCompartments.advance` and nothing else |
| `VenousBloodCompartment.advance` | `PatientCompartments.advance` and nothing else |
| `PatientCompartments.advance` | none |

Each advances one compartment against a fixed input, which was what a sub-step
of the split did. The coupled model no longer has such a thing: every rate is
evaluated from one state vector, and a caller who reached for
`tissue.advance()` would get a number that solves nothing in particular.

**Why they were not simply deleted with the rest.** Two reasons, and they point
opposite ways.

`BreathingCircuit.advance_fresh_gas` has a claim on staying:
`docs/MODEL.md` § "Breathing circuit" states its closed form as a documented
reduction of the model ("For constant input and no patient connection, the
exact v0.0.2 solution remains: ..."), and § "Required tests" requires the
preserved circuit reference tests that exercise it to keep passing.
`tests/reference/test_circuit_wash_in.py` is that gate.

The other four have no such claim - but each is covered by unit tests that
verify its own time constant against the analytic solution
(`tests/unit/test_tissue.py`, `test_blood.py`, `test_patient.py`), and deleting
them deletes that verification rather than moving it. Reaching the same
properties through the coupled system means zeroing the other flows and reading
one row, which is a weaker and less direct test than the one it would replace.

**Decision needed.** Which of three, and the middle one is probably right:

1. Delete all four with their tests, on the ground that a public mutator that
   can advance a compartment outside the governing equations is a way to reach
   a state that solves nothing.
2. Keep them as documented compartment primitives, and say so in each
   docstring - that they are the single-compartment closed forms, not how a run
   advances - so a reader cannot mistake one for the model.
3. Keep the two whose closed forms `docs/MODEL.md` states and delete
   `PatientCompartments.advance`, which is the only one of the five that is a
   *composition* rather than one compartment's own solution.

**Why it matters.** These are public methods on `core/` compartments, and what
`core/` offers publicly is what a future caller will reach for. Each of them
still *works* — it advances one compartment against a fixed input, exactly and
in isolation — so nothing about the call site would look wrong. What has changed
is that the model behind it is gone: after `PL-GS5X` every rate is evaluated
from one state vector, and a compartment advanced on its own is no longer a
sub-step of anything. A caller who wrote `tissue.advance(dt)` would get a
plausible number that solves no equation the simulator is running, which is the
shape `CLAUDE.md` reserves its "prefer an obvious failure to a plausible-looking
number" rule for. Nothing displayed today is wrong, because nothing in
production calls them — that is precisely why this is worth settling now, while
the answer costs a deletion rather than a bug.

The verification the tests carry is the other half, and it points the other way.
`tests/unit/test_tissue.py`, `test_blood.py` and `test_patient.py` check each
compartment's own time constant against the analytic solution. That is a direct
test of a closed form; reaching the same property through the coupled system
means zeroing the other flows and reading one row, which is weaker. So option 1
does not merely delete code, it trades a sharp verification for a blunt one, and
the decision has to be made with that on the table rather than as a dead-code
sweep.

**Where.** `core/circuit.py`, `core/tissue.py`, `core/blood.py`,
`core/patient.py`; `tests/unit/test_tissue.py`, `test_blood.py`,
`test_patient.py`, `test_circuit.py`; `tests/reference/test_circuit_wash_in.py`.
`PL-9SH6` renames across the same files and should be sequenced with whichever
answer is taken.

**Found.** Closing out `PL-GS5X`, 2026-09-06.

**Done when.** One of the three options above is chosen and applied to all five
methods, and `docs/MODEL.md` agrees with the result — either because the closed
forms it states are still reachable by the methods it implies, or because the
sentences naming them have been corrected. A method that survives carries a
docstring saying it is a single-compartment closed form and not how a run
advances; a method that goes takes its unit test with it only if the property
that test held is still verified somewhere. `PL-9SH6`'s renames land in the same
pass or immediately after it, not before.

**Decided 2026-09-13: option 3 — the three single-compartment closed forms
stay, documented; `PatientCompartments.advance()` goes. The line between the
two groups turned out to be measurable rather than a judgement call.**

**What the measurement was.** One 60 s step against six hundred 0.1 s steps,
on the sevoflurane reference patient at an arterial fraction of 0.08:

| Method | One 60 s step | 600 × 0.1 s | Relative difference |
| --- | --- | --- | --- |
| `BreathingCircuit.advance_fresh_gas` | — | — | 2.3e-14 |
| `TissueGroup.advance` | — | — | 1.1e-14 |
| `VenousBloodCompartment.advance` | — | — | 8.5e-16 |
| `PatientCompartments.advance` (mixed venous) | 0.018770 | 0.014969 | **0.254** |

The first three are exact at any step size, which is what a closed form means.
The fourth is a first-order operator split — it steps the three tissue groups
and then mixes their *end-of-step* return into venous blood, which is the
scheme `PL-GS5X` replaced — and it carried no documented error bound, no
production caller, and a docstring ("Advance tissues and venous blood") that
gave a reader nothing to suspect. That is the plausible-looking number
`CLAUDE.md` reserves "prefer an obvious failure" for.

**The criterion was already written down, in `alveolar.py`.** "Nothing outside
the governing equations may move agent between two modelled compartments."
Solving one compartment against a stated boundary input does not; composing
several of them does, and `PatientCompartments.advance()` moved agent from the
tissues into the venous pool. So this is `PL-LKRP`'s rule applied a second
time rather than a new one, and it decides the five methods without appeal to
taste.

**`BreathingCircuit.advance` stays as a name.** `docs/MODEL.md` § "Preserved
circuit reference tests" requires the v0.0.2 analytic tests to pass
*unchanged*, and `tests/reference/test_circuit_wash_in.py` calls the circuit by
that name. Its docstring now says so, instead of "Preserve the original v0.0.2
circuit interface" with no reason attached.

**Where the verification went, which is the half the brief was right to
insist on.** Six tests called the deleted method. Two properties moved *up* to
the coupled system, where both are stronger than they were:

- `test_mixed_venous_blood_lags_the_flow_weighted_tissue_return` — the
  patient-side step held the tissue return constant across a step, so it could
  only ever show the lag at the size of one step. Against the coupled run the
  return is rising continuously and the pool is chasing it.
- `test_higher_cardiac_output_increases_early_uptake_and_lowers_alveolar_fraction`
  — the compartment-level version could assert only the first half, because it
  took the arterial fraction as an argument. The fall in `F_A` is the feedback
  it structurally could not produce, and it is the half a learner is looking
  at.

`test_zero_cardiac_output_prevents_uptake` was already covered at the system
level by `tests/reference/test_sevo_patient.py::test_zero_cardiac_output_prevents_patient_uptake`,
which is `docs/MODEL.md`'s required zero-cardiac-output test; the duplicate
went. Two tests that only needed *a loaded patient* now load it with the
setters. `test_reported_change_matches_patient_storage` tested the deleted
method's own return contract and went with it.

The three survivors' verification is stronger than before, not merely
preserved: `tests/unit/test_compartment_primitives.py` holds the step-size
property for all three at once, where `test_blood.py` had never had one.

**`docs/MODEL.md` needed no edit, checked rather than assumed.** § "Breathing
circuit" states the closed form `advance_fresh_gas` implements and it is still
reachable; § "Tissue uptake and return" and § "Venous blood" state the two
ODEs and their time constants, both still implemented; § "Preserved circuit
reference tests" is unchanged and still passing. Nothing in `docs/MODEL.md`,
`docs/ARCHITECTURE.md` or `README.md` named `PatientCompartments.advance`.
`docs/ARCHITECTURE.md`:99 already said the step is "one exact propagation
rather than … a sequence of sub-exchanges", which this makes true of the
public surface as well as of the step.

**`PL-9SH6`'s renames are unblocked and land after this**, as the brief asked.
This pass renames nothing.
