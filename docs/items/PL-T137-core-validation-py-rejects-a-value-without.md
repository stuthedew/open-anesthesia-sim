---
id: PL-T137
title: core/validation.py rejects a value without naming it, where core/supported_ranges.py names the value, the supported range and where the range comes from
status: untriaged
feature: documentation-standard
touches: src/anesthesia_sim/core/validation.py, tests/unit/test_validation.py
added: 2026-09-05
---

**Problem.** The three shared guards raise on the parameter name alone:

    raise SimulationConfigurationError(f"{name} must be positive and finite")

so a rejected `gas_volume_l` of `-0.0`, `nan` and `-2.5` are indistinguishable
in the message. `core/supported_ranges.py:78` is the counter-example in the
same package and is what the standard should be — it names the value, the
range it fell outside, why that range is the range, and where to read more:

    f"{name} of {value} is outside the supported input range of "
    f"{minimum} to {maximum} L/min, which is the domain the model's "
    f"error bound is measured over (docs/MODEL.md, ...)"

**Why it matters.** Lee 2018 rule 9 asks an error message for what went wrong,
what the state was, and how to fix it. Here that is not a usability point: a
rejected setting reaches the interface, and `CLAUDE.md`'s safety-critical
standard requires a displayed value to be traceable to the inputs that
produced it — which a refusal that omits the input is not. `nan` and a
negative number also fail the same guard for different reasons and want
different fixes.

**Where.** `require_positive_finite`, `require_nonnegative_finite` and
`require_concentration_fraction` in `core/validation.py`; the tests that
assert on their message text.

**Done when.** Each guard's message carries the rejected value in the same
shape `supported_ranges.py` uses, and a non-finite value is distinguishable
from an out-of-range one. Consider whether one of the two shapes should be
shared rather than written twice.
