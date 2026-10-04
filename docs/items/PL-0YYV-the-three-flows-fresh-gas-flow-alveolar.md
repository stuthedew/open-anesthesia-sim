---
id: PL-0YYV
title: The three flows - fresh gas flow, alveolar ventilation and cardiac output - are bare floats range-checked by hand at each way in, so the way in nobody checked, UptakeEquationSettings, ran a cardiac output of 1000 L/min (PL-HSFV); slice 1 of PL-51B7 gives each a checked type built only through its require_supported_* guard, as SimulationStep is for the step
priority: P1
effort: L
status: ready
classes: refactor, safety
feature: parse-dont-validate
touches: src/anesthesia_sim/core/supported_ranges.py, src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/alveolar.py, src/anesthesia_sim/core/patient.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests, docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-10-04
payoff: no record or function in core/ or app/ can hold a flow outside its supported range, because the only way to make one is its guard, so a way in nobody thought to check - a settings record today, a saved run's loader later - is checked anyway
verify: grep -q 'fresh_gas_flow_l_min: FreshGasFlow' src/anesthesia_sim/core/governing_equations.py && grep -q 'alveolar_ventilation_l_min: AlveolarVentilation' src/anesthesia_sim/core/governing_equations.py && grep -q 'cardiac_output_l_min: CardiacOutput' src/anesthesia_sim/core/governing_equations.py
---

**Problem.** The three flows - fresh gas flow, alveolar ventilation and cardiac output - are bare floats range-checked by hand at each way in, so the way in nobody checked, UptakeEquationSettings, ran a cardiac output of 1000 L/min (PL-HSFV); slice 1 of PL-51B7 gives each a checked type built only through its require_supported_* guard, as SimulationStep is for the step

**Why it matters.** The supported ranges are the domain the model is claimed to
represent a patient over (`docs/MODEL.md` § "Supported input ranges"), and the
three flows are the settings a learner moves most. Checked by hand, every way in
has to remember three guards. The one that forgot, the settings record a
`RunDefinition` is built from, gave a precise-looking trace for a cardiac output
of 1000 L/min, a fresh gas flow of 500 L/min and an alveolar ventilation of
200 L/min (`PL-HSFV`, measured 2026-10-04). The step was checked the same way
and was captured eight times before `PL-0GJC` gave it a type (`PL-51B7` counts
them).

**What it is.** `PL-51B7`'s slice 1, as that item specifies it (project owner,
2026-10-04, ratified, over a range check in the settings record alone):

- `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput`, in L/min: `float`
  subclasses built only through their `require_supported_*` guard in
  `core/supported_ranges.py`, as `SimulationStep` is built through
  `require_supported_simulation_step`.
- A runtime check at each public entry point that refuses a bare `float`, as
  `require_simulation_step` does for the step, because `mypy` reads `src/` but
  not `tests/` and passes a value typed `Any`.
- `UptakeEquationSettings`'s three flow fields take the types, so the record
  `PL-HSFV` ran cannot be built, and neither `RunDefinition(...)` nor
  `record_change` can be handed one. The range check first built in that
  record's `__post_init__` (`c48a99be` on pull request 1342, reverted whole in
  `a8007351`) is not rebuilt.
- Every other signature and field in `core/` and `app/` that holds a flow takes
  its type: 28 annotated `float` across seven modules, `alveolar.py`,
  `circuit.py`, `governing_equations.py`, `patient.py`, `supported_ranges.py`,
  `uptake_system.py` and `app/controller.py`. Counted 2026-10-04 by annotation
  name, so a floor.
- The data files' `default_*_l_min` values are parsed into the types where the
  patient and the circuit are built from them, in `uptake_system.py` and
  `patient.py`.
- `docs/MODEL.md` § "Supported input ranges" says where each range is enforced.
  Its paragraph "Enforced on the compartment, not on the coupled system" ends
  "the compartment is the only point all three pass through", which this slice
  makes false.

Unchanged, as `PL-51B7` sets out: the tissue and venous blood flows, which no
supported-range guard bounds, and the circuit's deliverable-flow limit, the
machine's statement rather than the model's (`PL-8PS6`). The delivered
concentration is `PL-BBMG`'s and `PL-4R3W`'s.

**Size: L.** `PL-0GJC`'s build, pull request 1328, changed 32 files, adding 676
lines and removing 347, for 15 parameters and 2 fields, and was sized M. This
slice has 28 annotated signatures and fields in `src/`, 107 lines naming a flow
in `src/`, and 252 in 24 test files, counted 2026-10-04 by name.

**Classed `safety`, at `P1`.** It is the fix for `PL-HSFV`, a `P1` `safety`
defect, and the guard on three safety-critical inputs. Ranked below its own
defect, the work that closes it would wait behind ordinary `P2` items.

**How to start.**

1. Claim this item and `PL-HSFV` together; one pull request closes both, and
   every commit subject leads with both ids.
2. Read `PL-51B7`'s brief, then `PL-HSFV`'s § "Rebuilding as PL-51B7's slice 1",
   which says which of `c48a99be`'s tests to carry over and in what form.
3. Fetch them with `git fetch origin pull/1342/head`.

**Done when.** The three types exist and are built only through their guards;
`UptakeEquationSettings` types its three flow fields with them; every signature
and field in `core/` and `app/` that holds a flow takes its type, and each
public entry point refuses a bare `float` at runtime; the data defaults are
parsed into the types; `docs/MODEL.md` § "Supported input ranges" says where
each range is enforced; and `PL-HSFV`'s regression tests are in and that item
closes with this one.

**Gate.** On v0.6.0's frozen list, in the product lane, with the rest of the
`parse-dont-validate` feature (project owner, 2026-10-04). This item blocks
the other two slices, `PL-CN5S` and `PL-51B7`.
