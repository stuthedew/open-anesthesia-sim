---
id: PL-GKG4
title: Blood flow is a bare float checked by hand at three places in core (blood.py, tissue.py, governing_equations.py) and is not a checked type as cardiac output is, so the next function that takes one can skip the check
priority: P1
effort: M
status: ready
classes: defect, safety
touches: src/anesthesia_sim/core, tests/unit, tests/integration, docs/MODEL.md, docs/ARCHITECTURE.md, .claude/rules/core-domain.md
deferred-from: v0.7.0 - present at the freeze and not on the frozen list; found by the 2026-11-10 audit; not live: checked 2026-11-10, all three places that take a blood flow refuse a negative or non-finite one, so no wrong value is computed now
added: 2026-11-10
payoff: a blood flow is checked once where it is built, so a new function that takes one cannot skip the check
verify: grep -rq 'class BloodFlow' src/anesthesia_sim/core
reenters: PL-ZGYX
recurrences: 2026-11-11 PL-LHCL
---

**Problem.** Blood flow is a bare float checked by hand at three places in core (blood.py, tissue.py, governing_equations.py) and is not a checked type as cardiac output is, so the next function that takes one can skip the check

**Checked 2026-11-10:** `require_nonnegative_finite` is called on a `blood_flow_l_min: float` at three places: `time_constant_s` in `src/anesthesia_sim/core/blood.py`, `src/anesthesia_sim/core/tissue.py`, and `src/anesthesia_sim/core/governing_equations.py`. Cardiac output is a checked type, `CardiacOutput`. Not checked: whether any caller can pass a blood flow that did not come from a `CardiacOutput` and a `Fraction`, and so whether an upper limit is missing in practice. The audit's reviewer reported that `tests/unit/test_numerical_envelope_sweep.py` passes a blood flow of `sys.float_info.max`.

**Why it matters.** `.claude/rules/expert-review.md` asks that a quantity with a check of its own is checked once, by building a type that only the check produces. A check repeated at each way in fails at the one nobody guarded, as `PL-HSFV`'s settings record did. `docs/MODEL.md` says "Every input to the model has a range that includes its ends"; for blood flow the code enforces only that it is finite and not negative.

**Done when.** Blood flow is a checked type built from a cardiac output and a share, or by one check that states its range. The three functions take the type and no longer check a float. `docs/MODEL.md` states the range the type enforces, or says that blood flow is derived and has none of its own.

**Generator check.** An instance of `PL-ZGYX`'s fact (which values a quantity may take, and whether a number in hand was already checked against them), filed after that head closed on 2026-10-11. Its fix was a sweep that filed each way in as a member; blood flow stayed a float.

**Built 2026-11-11, as step (b) of `PL-LHCL`'s build order.**
`src/anesthesia_sim/core/blood_flow.py` holds two checked types.
`PerfusionFraction` is checked as above 0 and at most 1 when it is built.
`BloodFlow` is built only as a `PerfusionFraction` of a `CardiacOutput`, and
has no check of its own. The three hand checks are gone:

- `TissueGroup.time_constant_s` and `advance` take a `BloodFlow`, and
  `blood_flow_l_min_at` returns one.
- `VenousBloodCompartment.time_constant_s` and `advance` take the
  `CardiacOutput`, which is the pool's flow. The parameter is renamed from
  `blood_flow_l_min` to `cardiac_output_l_min`.
- `TissueGroupEquationSettings.blood_flow_l_min` is a `BloodFlow`. Its
  `_hold_as_exact_floats` helper is deleted, because the field now has one
  type in every record.

`TissueGroup.perfusion_fraction` and `ReferenceAdultParameters`' three
fractions are `PerfusionFraction`s. The note in `core/parameters.py` that kept
the perfusion fraction a bare `float` on the public side (`PL-KL2Q`) is
rewritten, because `PL-LHCL` decided the other way.

**Failed first.** `tests/unit/test_blood_flow.py` replays the report at the
three places, with 5e-324, 3.75 and the largest float. It uses only what
existed before the change. Against `main` at `e084968ac`, `uv run pytest -q -p
no:randomly tests/unit/test_blood_flow.py` gave `9 failed`, each with `Failed:
DID NOT RAISE TypeError`.

**Decided while building, each with one clearly better option.**

1. *A flow of 5e-324 L/min is still a flow.* It is the smallest perfusion
   fraction of 1 L/min. A smallest positive flow was refuted: zero flow is
   supported, the model is continuous down to it, and a gap between zero and
   a minimum would refuse values with nothing wrong in them. So
   `time_constant_s` returns `inf` where the quotient overflows, as at zero
   flow. A tissue stepped alone is then left unchanged, where the exact
   change over 24 hours is below 5e-296 L (largest envelope tissue: 1e4 L,
   tissue:gas 1e4, flow below about 3e-299 L/min). A test states this with
   the change worked out from the flow.
2. *A pickle or a copy rebuilds a flow as the whole of a cardiac output equal
   to it.* The flow stores neither factor. Storing them was refuted: it adds
   state that equality ignores and a write rule to guard it. The set of
   numbers the constructor can produce is exactly 0 to the largest cardiac
   output, so the rebuild proves what the original proved, and gives the same
   number bit for bit.
3. *The types live in their own module.* `core/supported_ranges.py` was
   refuted: `tests/unit/test_supported_range_edges.py` reads every `float`
   subclass there as built through a guard of the same parameter name, and
   `BloodFlow.__new__(cardiac_output_l_min, ...)` would have been read as the
   cardiac output's type.
4. *The perfusion fraction is its own type and not a `Fraction`.* A
   `Fraction` is a partial pressure and admits zero.

**What changed in behaviour.** A bare number where a blood flow or a
perfusion fraction belongs now raises `TypeError`, whatever its value. A
perfusion fraction outside its range is refused where it is built, with a
message that gives the value and cites `docs/MODEL.md` § "Tissue groups". The
earlier messages named only the field. No run changes: the matrix reads
`blood_flow_l_s`, a plain `float`, and the two sums of fractions add plain
`float`s as before (`float()` at three places, because CPython's `sum` adds a
`float` subclass without compensation, `PL-5BD7`).

**Still bare, and why.** `TissueGroupEquationSettings.blood_flow_l_s` and the
two `total_perfusion_fraction` returns are derived values, and are listed
under that reason in `tests/unit/test_bare_numbers.py`. The count there went
from 173 to 164.

**The range-edge test now draws the venous pool.** Its two methods take a
`CardiacOutput`, so `tests/unit/test_supported_range_edges.py` hands them
every cardiac-output edge. A tissue group's methods take a `BloodFlow`, which
no guard in that test's modules builds, so they are not drawn. That is step
(d) of `PL-LHCL`.
