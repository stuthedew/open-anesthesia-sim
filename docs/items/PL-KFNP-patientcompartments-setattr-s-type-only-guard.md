---
id: PL-KFNP
title: PatientCompartments.__setattr__'s type-only guard (PL-LBQY) admits a checked CardiacOutput written past set_cardiac_output and leaves every tissue's blood flow at the old output, a record the core refuses wherever it is next built; root cause of PL-M4M0 and the two items filed beside it, so decide whether the write keeps the relation through set_cardiac_output or is refused outright, which PL-LBQY's three options did not weigh (found reviewing PL-M4M0)
status: untriaged
feature: cardiac-output-write-consistency
added: 2026-10-11
root-cause-of: PL-M4M0, PL-VCP4, PL-J39J
generator: spent - every reader of the patient's output after the write has been walked: the step restates the record and Reset refuses it before clearing (PL-M4M0), a fork is refused by _disagreements_with, set_agent rebuilds through the setters, a setting change is PL-VCP4 and the readout PL-J39J; no control makes the write and mypy --strict refuses a bare float, so a new member needs a new reader of the output
misread: the output field is the cardiac output in force, where the tissue flows still hold the old one
---

**Problem.** PatientCompartments.__setattr__'s type-only guard (PL-LBQY) admits a checked CardiacOutput written past set_cardiac_output and leaves every tissue's blood flow at the old output, a record the core refuses wherever it is next built; root cause of PL-M4M0 and the two items filed beside it, so decide whether the write keeps the relation through set_cardiac_output or is refused outright, which PL-LBQY's three options did not weigh (found reviewing PL-M4M0)

**Context, 2026-10-11.** `PL-LBQY` (project owner, 2026-10-04, ratified, over
frozen compartments and over accepting the window) chose a `__setattr__`
guard that requires the field's type and nothing more, so
`patient.cardiac_output_l_min = CardiacOutput(6.0)` is admitted while every
tissue's `blood_flow_l_min` stays at its share of the old output, and
`UptakeEquationSettings` refuses the record wherever it is next built. Three
items are that one write seen from three readers: `PL-M4M0` (the record built
at Reset), `PL-VCP4` (the record built when another setting is recorded, after
that setter has written) and `PL-J39J` (the readout showing the written output
beside values computed at the old flows). Keeping the relation at the write -
`__setattr__` on that one field redistributing the flows as
`set_cardiac_output` does, or refusing the assignment and admitting only the
setter - was not among the three options `PL-LBQY` weighed, so this reopens a
ratified decision on ordinary evidence. No control makes the write and
`mypy --strict` refuses a bare float; what reaches it is a caller mypy does
not read, a test or a notebook, which is the caller `PL-LBQY`'s guard exists
for.

**Why it matters.** Each reader of the output after the write is a place the
screen can state a run the model never ran, and each has so far been found
one at a time.

**Done when.** A `CardiacOutput` assigned to `PatientCompartments
.cardiac_output_l_min` past `set_cardiac_output` either moves every tissue's
flow with it, so the record `UptakeEquationSettings` builds afterwards is the
one the setter would have left, or is refused at the assignment with a
message naming the setter; `tests/unit/test_supported_ranges.py` pins the
choice beside `PL-LBQY`'s test; `docs/MODEL.md` § "Supported input ranges"
says which; and `PL-VCP4` and `PL-J39J` are closed by it or re-scoped to what
it leaves.
