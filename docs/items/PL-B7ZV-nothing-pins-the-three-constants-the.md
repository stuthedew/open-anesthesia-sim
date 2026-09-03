---
id: PL-B7ZV
title: Nothing pins the three constants the conservation guard's sensitivity depends on
priority: P1
effort: S
status: done
classes: defect, safety, test
feature: numerical-domain
touches: tests/unit/test_agent_simulation_validation.py
added: 2026-09-03
closed: 2026-09-03
verify: uv run pytest tests/unit/test_agent_simulation_validation.py && grep -q 'def test_the_accounting_tolerances_are_the_documented_release_tolerances' tests/unit/test_agent_simulation_validation.py
---

**Problem.** `core/agent_simulation_validation.py` decides whether a run has
stopped conserving agent, and halts it if so. Three constants set how
sensitive that decision is:

```text
AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L = 1e-12
AGENT_ACCOUNTING_RELATIVE_TOLERANCE = 1e-9
MINIMUM_RELATIVE_SCALE_L = 1e-15
```

None of the three appears anywhere in `tests/`, `tools/` or `docs/MODEL.md`
under those names. Each can be moved by orders of magnitude with the whole
suite still green. Measured 2026-09-03 by mutating a scratchpad copy of `src/`
and running `tests/unit tests/reference tests/integration` in full:

| Mutation | Result |
| --- | --- |
| `AGENT_ACCOUNTING_RELATIVE_TOLERANCE` 1e-9 -> 1e-3 | 1169 passed, 0 failures |
| `AGENT_ACCOUNTING_ABSOLUTE_TOLERANCE_L` 1e-12 -> 1e-3 | 1169 passed, 0 failures |
| `MINIMUM_RELATIVE_SCALE_L` 1e-15 -> 1e3 | 1169 passed, 0 failures |

Those were the only survivors of a 24-mutation probe over `core/` and `app/`;
the other 21 - transposed volume weights, a 0.1% tissue time constant, a
conservative-but-wrong exchange rate, a removed vaporizer guard, a disabled
rollback - were all killed.

**Why it matters.** `docs/MODEL.md` § "Mass-balance identity" calls 1e-12 L
and 1e-9 *release tolerances*, and `require_valid_agent_accounting()` is what
stops a run whose numbers can no longer be trusted. A documented release
tolerance that no gate holds is `CLAUDE.md`'s own worst case: a check passing
while the guarantee it stands for is void. At the loosened relative tolerance
an 8 h case at the envelope corner delivers 384 L of agent, so 1e-3 relative
would admit 0.38 L unaccounted - roughly a fifth of the whole circuit and
alveolar store - without the guard firing or a single test objecting.

Nothing shipped is wrong: measured over 8 h at the corner the residual reaches
2.28e-9 L absolute and 5.9e-12 relative, about 170x inside the live guard. The
defect is that the margin rests on nobody having edited a constant, rather
than on anything that would notice.

**Why the existing tests do not close it.** `test_agent_simulation_validation.py`
tests errors of 0.05 L against a 1.25 L scale - a 4% relative error. So the
suite establishes "0% passes, 4% fails" and says nothing about where between
them the boundary sits, which is the only thing the three constants decide.
There is also no test of the abs-OR-rel disjunction, and none of the scale
floor.

**Where.** `src/anesthesia_sim/core/agent_simulation_validation.py:11-13`;
`tests/unit/test_agent_simulation_validation.py`; `docs/MODEL.md:487-491`.

**Approach.** Two tests, both in `tests/unit/test_agent_simulation_validation.py`:

1. A pinning test asserting the three constants against the values
   `docs/MODEL.md` documents, in the idiom this repository already uses twice -
   `test_envelope_limits_match_the_supported_input_ranges` and
   `test_displayed_resolution_and_shipped_step_match_the_interface` - with a
   failure message naming the MODEL.md section a deliberate change must revise.
2. Boundary cases either side of each threshold: a relative error of 9e-10
   passes and 1.1e-9 fails; an absolute error of 9e-13 passes and 1.1e-12
   fails with the relative branch out of reach; and a check with nothing
   delivered exercises `MINIMUM_RELATIVE_SCALE_L` rather than dividing by zero.

Deliberately test-side only. The constants and the guard are correct; what is
missing is anything that would notice them changing. `touches` therefore
avoids `core/`, which keeps the item delegable.

**Related.** `PL-4GN8` (the reference tests' `absolute_error_l <= 1e-12`
assertion tracks whichever dial its test runs at) is the same guarantee seen
from the reference suite; `PL-MS54` (MODEL.md quotes tolerance names that do
not exist in the code) is why a reader cannot find these constants from the
specification. Neither pins a value, so all three are separate work.

**Done when.** `tests/unit/test_agent_simulation_validation.py` fails if any of
the three constants is changed without the documented basis being revised with
it, and covers the boundary either side of both tolerance branches.

**Closed 2026-09-03.** Eight tests in
`tests/unit/test_agent_simulation_validation.py`: the pinning test the
`verify:` command names; four cases 10% either side of the two thresholds,
each asserting that the other branch of the disjunction is out of reach rather
than assuming it; two *at* the thresholds exactly; and one holding the scale
floor to being the denominator when nothing has been delivered.

The two exact-threshold cases are beyond the approach above, and they are what
closed the last surviving mutation: a comparison tightened from `<=` to `<`
moves the boundary by one float ulp, which the +/-10% cases cannot see, and
`docs/MODEL.md` § "Mass-balance test" states the condition inclusively. Both
are constructed so the residual is exact rather than rounded - a picolitre
delivered against an empty store for the absolute branch, and a litre
delivered against a litre exhausted with a nanolitre left over for the
relative one - which is what makes an equality boundary testable at all.

Re-ran the probe that found this. All twelve mutations now fail the file,
against three survivors before: each of the three constants moved by a single
decade as well as by the orders of magnitude originally measured, the
disjunction turned into a conjunction, either comparison tightened from `<=`
to `<`, the scale floor removed, `abs()` replaced by `max(_, 0.0)` so extra
agent goes unseen, and `require_valid_agent_accounting()` made to never raise.

Nothing under `src/` changed, and the two related items stay open:
`PL-MS54` (MODEL.md quotes tolerance names that do not exist in the code) is
still why a reader cannot find these constants from the specification, and
`PL-4GN8` (the reference suite's own `1e-12` assertion) is the same guarantee
seen from `tests/reference/`.
