---
id: PL-V10T
title: Each supported-range guard is tested at the edge values its author thought of, so the overflow class behind PL-YZ17, PL-5F76 and PL-BPRK was found one function at a time: generate IEEE 754 edges across every range core/supported_ranges.py declares, and assert a finite result or the simulator's own error
priority: P2
effort: M
status: blocked
classes: test
feature: numerical-domain
touches: pyproject.toml, uv.lock, tests/unit/test_supported_range_edges.py
blocked-by: PL-0GJC
added: 2026-10-03
payoff: a value a supported-range guard accepts but the function behind it cannot compute with fails a test when the function is written, instead of escaping as a raw OverflowError or ValueError found one function at a time
---

**Problem.** Each supported-range guard is tested at the edge values its author thought of, so the overflow class behind PL-YZ17, PL-5F76 and PL-BPRK was found one function at a time: generate IEEE 754 edges across every range core/supported_ranges.py declares, and assert a finite result or the simulator's own error

**Found 2026-10-03**, beside `PL-0GJC`, answering the project owner's question
how to stop the day's predictable failures recurring. Three captures that day
are one class found in three functions: `PL-YZ17` (86 400 s divided by a step
below about 4.8e-304 s is `inf`, and flooring it raises `OverflowError`),
`PL-5F76`'s count half (`str()` of an integer past 4,300 digits raises
`ValueError`, CPython's integer-string conversion limit) and `PL-BPRK` (two
more functions overflowing the same way). In each, a guard accepted a value the
function behind it could not compute with.

The tests already reach for IEEE 754 edges by hand. Counted on `main` at
`7a6ec289`: `inf` appears in 14 test files, `nan` in 12, `nextafter`,
`5e-324` or `float_info` in 7, and no test builds an integer of 1,000 digits or
more. Each edge was written for the guard in front of its author, so a function
nobody guarded has no edge test either; `PL-WP52`'s compartments are the
instance.

**Why it matters.** The guards stand in front of the simulator's clinical
arithmetic, and every instance of this class so far was found by somebody
trying the value after the function had shipped: three on 2026-10-03 alone,
in three functions. A guard's own tests say nothing about a function written
after it, so each new function behind a guard is a new chance for the class,
and each instance found that way costs a capture, a triage and a fix. The
class is still live. On `main` at `48787726`, 2026-10-04,
`SimulationState(step_count=10**5000, simulation_step_s=0.1)` raises the
builtin `ValueError` ("Exceeds the limit (4300 digits) for integer string
conversion") rather than `SimulationConfigurationError`, which is `PL-5F76`'s
open half. Checked at the same commit: `hypothesis` appears in neither
`pyproject.toml` nor `uv.lock`, no test imports it, and the seven guards are
the ones named below.

**The property to test**, whichever tool runs it: every value a guard accepts,
each function behind that guard computes with, and every value it refuses
raises the simulator's own error. Neither `OverflowError`, `ValueError` nor
`ZeroDivisionError` escapes. The guards are the six `require_supported_*`
functions in `src/anesthesia_sim/core/supported_ranges.py` and
`require_supported_simulation_step`, which is not in that module: #1328 moved
it from `uptake_system.py` to `core/simulation_step.py`. Which functions sit
behind which guard was a list someone kept; with `PL-0GJC`'s `SimulationStep`,
which #1328 landed in that module, it is every function annotated with it,
which `typing.get_type_hints` finds.

**Decided 2026-10-03: yes** (project owner, 2026-10-03, ratified, over a
shared edge-value table that adds no dependency): Hypothesis joins the dev
dependencies, with the known edges as explicit examples and the runs
derandomized.

**Recommended:** property-based tests with Hypothesis, added as a dev
dependency, drawing values across and beyond each range, with the edges above
written as explicit examples that always run, and derandomized so a red run
reproduces exactly and the suite stays deterministic. NumPy, SciPy and Astropy
all test with it: NumPy as an optional test dependency, and SciPy and Astropy in
their `pyproject.toml` test requirements, read from each repository's default
branch on 2026-10-03.

The alternative needs no dependency: one shared table of edge values in a test
helper, applied to each guard. It is deterministic and auditable, and it would
have caught all three captures, but it finds only the values it lists. The
trade is one maintained dependency against the next class nobody listed.

[superseded 2026-10-03: the decision above, and the Done-when below]
**Done when.** The owner has chosen between the two, and the chosen one checks
the property above for every guard, finding the guards and what they protect
rather than listing them, so a new range is covered without editing the test.

**Blocked on `PL-0GJC`** (triage, 2026-10-04). Its `SimulationStep` type is
how this test finds the functions behind the step guard: every function
annotated with it. Built before that type lands, the test would keep the list
by hand, which the Done-when below refuses. #1328 landed the type (checked
2026-10-04: parameters and returns annotated with it in six modules), but
`PL-0GJC` stays open, at `needs-decision`, on whether the compartments take it
or a second, floor-only type. That answer sets which types this test finds
functions by, so the wait holds until `PL-0GJC` closes.

**Done when.** Hypothesis is a dev dependency in `pyproject.toml`, locked in
`uv.lock`, and `tests/unit/test_supported_range_edges.py` checks the property
above for every guard. Values are drawn across and beyond each range, the
edges named above are explicit examples that always run (the infinities, NaN,
the subnormals, the largest float, each range's bounds and their neighbours,
and an integer past 4,300 digits where a guard takes a count), and every run
is derandomized. The test finds the guards and the functions behind each
rather than listing them, so a guard added to `core/supported_ranges.py` is
drawn without editing it, and it is named
`test_each_guard_admits_only_what_its_functions_compute`.

**Generator check.** Not owed: no `touches` path is under `workflow_paths`.
For `PL-74T0`'s cluster 3 (the supported step, guarded entry point by entry
point) this is the tests' side. It catches a member among the functions it
finds, while stopping an unguarded entry point is `PL-0GJC`'s type's work, so
it is no head's fix.
