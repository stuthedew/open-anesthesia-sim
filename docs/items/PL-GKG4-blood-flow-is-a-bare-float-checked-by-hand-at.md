---
id: PL-GKG4
title: Blood flow is a bare float checked by hand at three places in core (blood.py, tissue.py, governing_equations.py) and is not a checked type as cardiac output is, so the next function that takes one can skip the check
priority: P1
effort: M
status: ready
classes: defect, safety
touches: src/anesthesia_sim/core/blood.py, src/anesthesia_sim/core/tissue.py, src/anesthesia_sim/core/governing_equations.py, tests/unit, docs/MODEL.md
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
