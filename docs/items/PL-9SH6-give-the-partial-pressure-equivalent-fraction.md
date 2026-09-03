---
id: PL-9SH6
title: Give the partial-pressure-equivalent fraction one accessor name across every compartment in core/
priority: P2
effort: M
status: ready
classes: refactor
feature: core-domain-language
touches: src/anesthesia_sim/core, src/anesthesia_sim/app, tests
added: 2026-09-03
verify: uv run pytest -q tests/unit/test_alveolar.py tests/unit/test_blood.py tests/unit/test_circuit.py tests/unit/test_patient.py tests/unit/test_tissue.py && grep -q 'def partial_pressure_fraction' src/anesthesia_sim/core/alveolar.py
---

**Problem.** `docs/MODEL.md` § "Concentrations" states that every model
concentration is one kind of thing: "dimensionless partial-pressure-equivalent
fractions from 0 through 1". `core/` gives that one quantity eight names.

| Symbol | Today | Uses (src / tests) |
| --- | --- | --- |
| $`F_D`$ | `BreathingCircuit.delivered_concentration_fraction` | 36 / 58 |
| $`F_C`$ (see below) | `BreathingCircuit.circuit_concentration_fraction` | 24 / 52 |
| $`F_A`$ | `AlveolarCompartment.concentration_fraction` | 19 / 17 combined |
| $`F_v`$ | `VenousBloodCompartment.concentration_fraction` | ” |
| $`F_v`$ | `PatientCompartments.mixed_venous_fraction` | 3 / 6 |
| $`F_i`$ | `TissueGroup.partial_pressure_fraction` | 13 / 11 |
| $`F_i`$ | `TissueGroup.venous_outflow_fraction` | 2 / 0 |
| $`F_a`$ | `arterial_fraction` (argument only) | 11 / 15 |
| $`F_{\text{tissue return}}`$ | `PatientCompartments.tissue_return_fraction` | 8 / 5 |

Counted 2026-09-03 with `grep -rnow` over `src/` and `tests/`.
`concentration_fraction` covers three different symbols and
`partial_pressure_fraction` a fourth, with nothing distinguishing them; and
`BreathingCircuit.circuit_concentration_fraction` stutters, since the class
already says circuit.

**Why it matters.** This is the defect planned-milestone item 29 exists to fix,
stated concretely. A reader who knows uptake and distribution meets
`concentration_fraction` on three classes and has to open each one to learn
which $`F`$ it is — the translation step `.claude/rules/core-domain.md` names.

The question of whether the gas compartments should say "concentration" and the
blood and tissue compartments "partial pressure" was raised in the scoping round
and is settled against: Hendrickx and De Wolf state that "in the gas phase,
either 'fraction,' 'concentration,' or 'partial pressure' can be used", so a
convention marking that distinction would encode one the domain declines to
make. Partial pressure is also the physically correct choice for a single name,
because it is the quantity continuous across the phase boundaries this model
steps across, where concentration jumps by $`\lambda`$.

**The rule.** `_partial_pressure_fraction` is the suffix, always, and it names
the kind. A prefix appears only where one object holds more than one such
quantity — which is `BreathingCircuit` alone, holding both $`F_D`$ and the
inspired fraction. Everywhere else the object supplies the subscript, so the
accessor is bare:

| Symbol | After |
| --- | --- |
| $`F_D`$ | `BreathingCircuit.delivered_partial_pressure_fraction` |
| $`F_I`$ | `BreathingCircuit.inspired_partial_pressure_fraction` |
| $`F_A`$ | `AlveolarCompartment.partial_pressure_fraction` |
| $`F_v`$ | `VenousBloodCompartment.partial_pressure_fraction` |
| $`F_v`$ | `PatientCompartments.mixed_venous_partial_pressure_fraction` |
| $`F_i`$ | `TissueGroup.partial_pressure_fraction` (unchanged) |
| $`F_a`$ | `arterial_partial_pressure_fraction` (argument) |
| $`F_{\text{tissue return}}`$ | `PatientCompartments.tissue_return_partial_pressure_fraction` |

**`venous_outflow_fraction` is not dead code, and deleting it is a judgment.**
It has exactly one caller, `patient.py:108`, inside `tissue_return_fraction`,
and it returns `partial_pressure_fraction` unchanged. It is therefore an alias
that states a piece of physiology — the blood leaving a perfusion-limited tissue
is in equilibrium with that tissue — at the one site where that fact is being
relied upon. Weigh keeping it, with a docstring saying that is its job, against
folding it into the caller with a comment. Do not delete it silently as a
duplicate.

**Where.** `core/alveolar.py`, `core/blood.py`, `core/circuit.py`,
`core/patient.py`, `core/tissue.py`, `core/uptake_system.py`; then
`app/controller.py` and `app/simulation_view.py`; then the twelve test modules
that name these accessors. Roughly 300 sites.

**This is a rename and nothing else.** No equation, parameter, numerical method
or displayed value changes, and the full suite must pass unchanged — that
property is what makes a diff this wide reviewable, so do not fold any other
change into it. `PL-KZS3` (the circuit's stored primitive) is deliberately
excluded for exactly this reason.

**Sequencing.** After `PL-H46J` (the Symbols Code column), which fixes the
target vocabulary. `PL-3TLK` supplies the $`F_C \rightarrow F_I`$ half of the
table above together with the MODEL.md assumption it depends on; the two land in
one commit.

**Sequencing changed 2026-09-03.** Now behind `PL-GS5X` (the exact matrix
exponential), which deletes `_exchange_circuit_and_alveoli` and restructures
`AgentUptakeSystem._advance_step`. Renaming that code first is work thrown
away, and the counts in the table above will be smaller once it lands —
re-measure rather than trusting them. Still after `PL-H46J`.

**Done when.** One accessor name denotes the partial-pressure-equivalent
fraction throughout `core/`, `app/` and `tests/`, per the table above; the
`venous_outflow_fraction` decision is recorded in the code; `make check` passes;
and no test's expected value changed.

**Two more items in the sequence (added 2026-09-03).** The Sequencing section
above names `PL-H46J`, `PL-3TLK`, `PL-GS5X` and `PL-KZS3`. Two app-layer items
belong in it too, and both run *before* this one:

- `PL-WB0X` (split `simulation_view.py`) **has landed** - merged 2026-09-03 as
  #263, taking the view from 1265 lines to 1054 - which is the good order and
  removes the risk of this rename landing inside a class about to be split. It
  also moved this item's app-layer surface without shrinking it: the six sample
  accessors are now free functions in `app/chart_series.py:76-96`, each
  returning one of the fields the table above renames, and `app/formatting.py`
  is a third app file to sweep. Re-measure against the current tree, not against
  the counts in the table.
- `PL-W3DD` (key `SimulationHistorySample` by substance) reshapes six of the
  accessors named in the table above out of existence as separate fields.

The warning already written here - "the counts in the table above will be
smaller once it lands, re-measure rather than trusting them" - was written about
`PL-GS5X` and applies at least as strongly to these two.