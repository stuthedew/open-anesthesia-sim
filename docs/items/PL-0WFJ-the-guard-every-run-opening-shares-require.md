---
id: PL-0WFJ
title: The guard every run opening shares, require_canonical_state, checks a state's length, finiteness and unit entry but no physical range, so a RunDefinition opened from a state with an alveolar fraction of -0.3 and a fat fraction of 1.7 accepts it and returns negative and above-one fractions from state_at and evaluate_anchored without any error, while the live system refuses the same state
priority: P1
effort: S
status: ready
classes: defect, science, safety
feature: replay-findings
touches: src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/run_definition.py, tests/unit/test_governing_equations.py, tests/unit/test_run_definition.py
added: 2026-10-25
payoff: a physically impossible opening state fails visibly instead of drawing plausible traces, before saved runs can be loaded
verify: grep -q 'def test_require_canonical_state_refuses_a_fraction_outside_zero_to_one' tests/unit/test_governing_equations.py
---

**Problem.** `RunDefinition.__init__` checks its opening state through `_require_state` (`src/anesthesia_sim/core/run_definition.py`). That calls `require_canonical_state` (`src/anesthesia_sim/core/governing_equations.py`). The guard checks the type, the length, finiteness and the unit entry. It does not check that each fraction lies from zero to one, or that the two accumulators are not negative. The live system's resume path checks both. It builds each fraction as a `Fraction` and checks the accumulators as nonnegative (`src/anesthesia_sim/core/uptake_system.py`). So the two sinks disagree about what a valid state is. The guard's own docstring says sharing one guard keeps them from disagreeing.

**Why it matters.** Today every opening state comes from a run that began in range, so a learner cannot reach this. Saving, loading and replaying a run will open a definition from a state that did not come from the stepped core. A physically impossible state would then draw plausible-looking traces instead of failing. `CLAUDE.md`'s safety standard asks for an obvious failure in that case. The fix is to check the ranges in `require_canonical_state`, so both sinks refuse the same states.

**Done when.** `require_canonical_state` refuses a state with a fraction outside zero to one or a negative accumulator, so `RunDefinition` and the live system refuse the same states. `tests/unit/test_governing_equations.py` has `test_require_canonical_state_refuses_a_fraction_outside_zero_to_one`.

**Found by.** `PL-TBQS` reviewer replay on #430, finding 430 r05 F2, checked against main on 2026-10-25. Reproduced with `scratchpad/r/scripts/d_430_core.py`: the definition accepted the state, and `state_at(30.0)` returned a fat fraction of 1.6996, a circuit fraction of -0.0296 and an alveolar fraction of -0.0606.

**Also the last input without an interval, 2026-10-26.** `PL-58D7`'s corner
sweep and its blind review found that this guard is the one input to `core/`
with no interval. From an opening state with every fraction at 1e308 at a
10 000 L corner with the widest flows, `state_at(600.0)` returned fractions
near 1e307 and an exhausted-agent total of `inf`, with no error. So
`PL-58D7` is blocked on this item and lists it as a member. When it lands, add
the opening state to the table in `docs/MODEL.md` § "The numerical envelope".
