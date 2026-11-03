---
id: PL-NYFZ
title: A test tolerance smaller than the gap between neighbouring floating-point numbers at the compared value turns an approximate check into an exact one without saying so (Error Prone's FloatingPointAssertionWithinEpsilon flags this in Java); nothing here checks for it in the simulator's tests (found while researching PL-TN0G)
priority: P3
effort: S
status: done
classes: test
feature: dead-test-limits
touches: tests/conftest.py, tests/unit/test_tolerance_spacing.py, .claude/rules/test-oracles.md, docket.toml
added: 2026-11-03
closed: 2026-11-03
pr: 1974
payoff: a test limit that silently demands an exact match fails at once with the two numbers and both fixes, so no reader is told a check tolerates rounding it never tolerates
verify: grep -q 'def test_a_tolerance_below_the_spacing_fails' tests/unit/test_tolerance_spacing.py && grep -q 'def refuse_tolerances_below_spacing' tests/conftest.py
---

**Problem.** A test tolerance smaller than the gap between neighbouring floating-point numbers at the compared value turns an approximate check into an exact one without saying so (Error Prone's FloatingPointAssertionWithinEpsilon flags this in Java); nothing here checks for it in the simulator's tests (found while researching PL-TN0G)

**Why it matters.** A limit such as `pytest.approx(100.0, abs=1e-15)` reads as
"allow rounding error", but the nearest other floating-point numbers to 100.0
are 1.42e-14 away, so only 100.0 itself can pass. The reader is told the check
tolerates a difference it never tolerates. A harmless change in the order of
the arithmetic then fails the test, and the writer who widens the limit cannot
tell from the test whether the exact match was meant. Rule 7 of
`.claude/rules/test-oracles.md` asks every numerical limit to say how large the
rounding it allows is, and a limit below the spacing allows none. Error Prone
flags the same mistake in Java as `FloatingPointAssertionWithinEpsilon`: a
nonzero tolerance smaller than the smaller of the two gaps to the expected
value's neighbours
(https://raw.githubusercontent.com/google/error-prone/master/core/src/main/java/com/google/errorprone/bugpatterns/FloatingPointAssertionWithinEpsilon.java,
read 2026-11-03).

**Generator check.** A one-off. The fact misread is the spacing between
floating-point numbers at a test's expected value, which no tool records, and
`bin/docket generators` names no head reading it. The measurement below finds
no instance in the suite today.

**Measured 2026-11-03, on `main` at `a7806459`.** A throwaway pytest plugin
recorded every tolerance comparison in one run of `tests/unit`,
`tests/reference` and `tests/integration` (8,712 tests, all passing). It
recorded, per call site, the smallest ratio of the tolerance to the spacing at
the expected value.

- `pytest.approx`: 40,663 element comparisons at 384 call sites. None is below
  the spacing. The closest are `rel=1e-15` on 0.02, 0.08 and 0.013
  (`tests/unit/test_circuit.py:1201`, `tests/unit/test_tissue.py:701`,
  `tests/unit/test_blood.py:469`), at 5.8 to 7.5 times the spacing, and
  `abs=1e-15` on 0.5 and 1 in `tests/unit/test_layout_model.py`, at 9 times.
  The same `abs=1e-15` on any value of 8 or more would be exact.
- `math.isclose`: 1,142 calls at 68 sites, none below the spacing.
- Hand-written bounds, `assert abs(a - b) < limit` or `<= limit`: 51 sites,
  none below the spacing. The five closest, at 1 to 3 times, are deliberate
  bounds of one to three units in the last place, written with `math.ulp`
  (`tests/unit/test_resume_at.py:200`, `tests/unit/test_exponential_approach.py`).
  The next closest is `tests/integration/test_controller.py:2604`, 1e-14 on a
  delivered amount of 0.28 L, at 180 times. It would become exact once the
  delivered amount passed 64 L.

The plugin was checked first on a scratch test holding one planted case of
each kind, and it named all four.

**Design** (session decision, 2026-11-03).

1. **A check inside every test run.** `tests/conftest.py` wraps the
   comparison inside `pytest.approx` (`_pytest.python_api.ApproxScalar`) and
   `math.isclose` when pytest configures. A
   comparison whose nonzero tolerance is smaller than the spacing at its
   expected value fails the test, with a message naming the tolerance, the
   spacing, and the two fixes: `==` for an exact check, or a limit of at
   least the spacing. It reads the tolerance from pytest's own
   `ApproxScalar.tolerance`, so pytest's rule for combining `rel` and `abs`
   is not written a second time. It fails rather than warns, because the
   rule is exact: such a limit is always an exact check, whatever the test
   meant. `math.isclose` is checked only when a file under `tests/` calls it,
   because the simulator's own calls are not a test's limit.
2. **Hand-written bounds are left to rule 7, not to the check.** pytest offers
   no hook into `abs(a - b) < limit`. Reaching one would mean rewriting every
   `assert` in the suite at import, through a second private pytest
   interface, and changing the failure message of each. The measured margins
   above are 180 times or more, apart from the deliberate bounds in units in
   the last place. So rule 7 gains one sentence: a limit at the size of
   rounding error is written as a multiple of `math.ulp` of the compared
   value, or as a relative limit, never as a bare absolute number. Error
   Prone also reaches only the assertion libraries' own comparisons.
3. **The spacing** at a finite value x is the smaller of the gaps from x to
   `math.nextafter(x, inf)` and to `math.nextafter(x, -inf)`, as in Error
   Prone. At a power of two the gap below is half the gap above, so
   `math.ulp`, which gives the gap above, would overstate it there. A
   tolerance equal to the spacing still admits a neighbour, so only a
   tolerance strictly below it fails. A tolerance of zero is an exact check
   written on purpose, and passes.

**Done when.** A `pytest.approx` or `math.isclose` comparison in any test under
`tests/` whose nonzero tolerance is below the spacing at its expected value
fails that test with a message naming both numbers, and
`tests/unit/test_tolerance_spacing.py` pins that, the boundary at the spacing,
a power of two, a zero tolerance, pytest's default tolerance, and an
`isclose` called from outside `tests/`. Rule 7 of
`.claude/rules/test-oracles.md` carries the sentence on hand-written limits.

**Built 2026-11-03.** The check is in `tests/conftest.py` and runs in every
test run. `make check` passed with it installed, 12,020 tests, which agrees
with the measurement: no tolerance in the suite is below the spacing today.
