---
id: PL-KFNP
title: PatientCompartments.__setattr__'s type-only guard (PL-LBQY) admits a checked CardiacOutput written past set_cardiac_output and leaves every tissue's blood flow at the old output, a record the core refuses wherever it is next built; root cause of PL-M4M0 and the two items filed beside it, so decide whether the write keeps the relation through set_cardiac_output or is refused outright, which PL-LBQY's three options did not weigh (found reviewing PL-M4M0)
priority: P1
effort: M
status: needs-decision
classes: safety, defect
feature: cardiac-output-write-consistency
touches: src/anesthesia_sim/core/patient.py, tests/unit/test_supported_ranges.py, tests/integration/test_controller.py, tests/integration/test_simulation_view.py, tests/unit/test_uptake_system_failure.py, docs/MODEL.md
added: 2026-10-11
root-cause-of: PL-M4M0, PL-VCP4, PL-J39J
generator: spent - every reader of the patient's output after the write has been walked: the step restates the record and Reset refuses it before clearing (PL-M4M0), a fork is refused by _disagreements_with, set_agent rebuilds through the setters, a setting change is PL-VCP4 and the readout PL-J39J; no control makes the write and mypy --strict refuses a bare float, so a new member needs a new reader of the output
misread: the output field is the cardiac output in force, where the tissue flows still hold the old one
recurrences: 2026-10-12 PL-HQF5 withdrawn 2026-10-12 PL-HQF5
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

**Generator check.** Recorded at capture: `root-cause-of: PL-M4M0, PL-VCP4,
PL-J39J`, with `generator: spent` naming the readers walked. Confirmed at the
2026-10-12 triage pass; nothing to add.

**Decision needed** (the owner's: it reopens `PL-LBQY`, ratified 2026-10-04,
on ordinary evidence). Whether a `CardiacOutput` assigned to
`PatientCompartments.cardiac_output_l_min` past `set_cardiac_output` is refused
at the assignment, or moves every tissue's flow as the setter does.
**Recommendation: refuse it, with a message naming `set_cardiac_output`.** An
assignment that silently redistributes six tissue flows is a hidden mode - one
write doing a setter's work - and the safety standard prefers an obvious
failure to a record quietly rebuilt; refusing leaves one way to change the
output, the one the controller already uses. It extends `PL-LBQY`'s guard on
this one field rather than replacing it, so frozen compartments stay refused as
decided. `PL-VCP4` and `PL-J39J` are `blocked` on this item, and either answer
makes both unreachable through this write.

**Design round, 2026-10-12** (Order item 42 of the v0.6.0 Projects trial, on
`.claude/skills/docket/modes/design.md`). The question above stays the
owner's: the safety-critical standard reaches it, and it widens what the guard
`PL-LBQY` ratified checks on one field. Everything that follows from either
answer was decided here, so the build has no open call of its own.

**The count behind the recommendation.** Refusing is wrong only if some
caller needs an assignment that moves the flows, and the tree holds none.
Every write to the field in `src/` is the constructor's, `from_parameters`'s
or `set_cardiac_output`'s, and the three places outside `src/` that write it -
`_with_stale_tissue_flows` in `tests/integration/test_controller.py` and in
`tests/integration/test_simulation_view.py`, eight callers between them, and
`test_a_stale_record_met_at_step_time_is_a_failed_step_stated_in_litres_per_minute`
in `tests/unit/test_uptake_system_failure.py` - want the stale record, not a
redistribution: each exists to reach a record the step restates or Reset
refuses (`PL-M4M0`). Redistributing would also make this the one assignment in
the core that does a setter's work, where `PL-19Y0` is holding every other
direct write to what the record's constructor checks and nothing more, and it
would need a guard that knows whether the compartments exist yet, since the
constructor writes the output before them.

**Decided in the round: the shape of the refusal.** The record's own relation,
the one `__post_init__` checks, checked at the write. On a *rewrite* of
`cardiac_output_l_min`, `__setattr__` runs `_require_perfused_at` over the
three tissues and the venous pool against the value written, and refuses with
`SimulationConfigurationError` in the constructor's words, which already name
`set_cardiac_output` as the way to change the output; nothing is written when
it is refused. A *first* write is admitted on its type alone, as now, because
there are no compartments yet to compare against: the constructor,
`dataclasses.replace`, `copy.copy`, `copy.deepcopy` and a pickle each write the
output before any compartment (measured 2026-10-12 on a `slots=True` dataclass
of the same shape under CPython 3.14.7), and `__post_init__` then refuses a
copy made at another output as it does today (`PL-Z0T3`). So "is this a
rewrite" - `hasattr(self, name)` on the slot - is the whole condition, with no
flag saying who is writing and no `object.__setattr__` in the setter. A
rewrite to the output the compartments already stand at is admitted, since the
guard holds the relation and not the writer. Refused over a flag
`set_cardiac_output` sets around its own write, which refuses even a
consistent write and adds a mode to the class, and over `object.__setattr__`
in the setter, which `PL-LBQY` counted against freezing on the bar
`.claude/rules/core-domain.md` sets.

**Decided in the round: the setter's order.** `set_cardiac_output` requires
the type first (`require_cardiac_output`, the pattern's `require_*` at a public
entry point), perfuses the compartments at the new output, then writes the
field, so the write is admitted by the relation the guard holds and a refused
type moves nothing. `_update_blood_flows` takes the output it perfuses at
rather than reading the field. Nothing in the setter can raise once the first
compartment has moved: a `CardiacOutput` times a perfusion fraction is
nonnegative and finite, which is all `TissueGroup.set_blood_flow` and
`VenousBloodCompartment.set_blood_flow` require.

**Decided in the round: the tests that reach the stale record.** The nine
callers above keep their names, and `PL-M4M0`'s `verify:` stands. Each helper
reaches the record through a tissue's `set_blood_flow` instead, which remains
a way to a record the step restates and Reset refuses, because a tissue group
does not know its patient. The literal figures those tests assert in the
refusal change with the flow the helper moves, and are the build's.

**Decided in the round: what either answer leaves.** Neither makes the stale
record unreachable. `TissueGroup.set_blood_flow` and
`VenousBloodCompartment.set_blood_flow` set a compartment's flow past its
patient's output, nothing in `src/` but `_update_blood_flows` calls either,
and `PL-19Y0` holds a direct write to the field to sign and finiteness, not to
the patient's relation. So `PL-VCP4` and `PL-J39J` are re-scoped to a record
reached that way rather than closed, and stay blocked on this item because the
helper the build re-points is the one their tests would extend; the door
itself is `PL-HQF5`, filed under this feature, and the build need not reason
from "unreachable". `touches` is widened to the three test files the build
re-points.

**Bearing on `PL-19Y0`.** The same rule - a direct write held to what the
record's constructor checks - at a fourth record, and no shared file unless
`PL-19Y0` freezes `TissueGroup` or `VenousBloodCompartment`, which would reach
`_update_blood_flows` here. The circuit's fresh gas flow against the machine's
deliverable range is the same shape on a flow field and outside `PL-19Y0`'s
list: `set_fresh_gas_flow` and the constructor refuse it through
`_require_deliverable_flow`, and the field's `__setattr__` requires the type
alone. It binds nothing while no shipped profile declares a range, and is
`PL-5GVL`, filed under `parse-dont-validate`.

**Done when, under the recommendation** (takes effect with the answer). A
`CardiacOutput` written onto `PatientCompartments.cardiac_output_l_min` past
`set_cardiac_output` is refused at the assignment with a
`SimulationConfigurationError` naming `set_cardiac_output`, and the field and
every compartment's flow hold what they held, so the record
`UptakeEquationSettings` builds afterwards is the one the setter last left;
`set_cardiac_output` perfuses the compartments at the new output before it
writes the field, and a refused type moves nothing;
`test_a_cardiac_output_written_past_set_cardiac_output_is_refused_at_the_write`
in `tests/unit/test_supported_ranges.py` pins the refusal, the unchanged
flows, the consistent rewrite admitted, and the constructor, `replace`, copy
and pickle still writing the output first, beside `PL-LBQY`'s test; the two
`_with_stale_tissue_flows` helpers and the unit test above reach the stale
record through a tissue's `set_blood_flow`; `docs/MODEL.md` § "Supported
input ranges" and § "Reset" no longer call this the one write the type-only
guard admits and say what the write meets instead; and `PL-VCP4` and
`PL-J39J` are re-scoped as above.
