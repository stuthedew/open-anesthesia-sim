---
id: PL-V10T
title: Each supported-range guard is tested at the edge values its author thought of, so the overflow class behind PL-YZ17, PL-5F76 and PL-BPRK was found one function at a time: generate IEEE 754 edges across every range core/supported_ranges.py declares, and assert a finite result or the simulator's own error
status: untriaged
feature: numerical-domain
added: 2026-10-03
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

**The property to test**, whichever tool runs it: every value a guard accepts,
each function behind that guard computes with, and every value it refuses
raises the simulator's own error. Neither `OverflowError`, `ValueError` nor
`ZeroDivisionError` escapes. The guards are the six `require_supported_*`
functions in `src/anesthesia_sim/core/supported_ranges.py` and
`require_supported_simulation_step` in `uptake_system.py`, which is not in that
module. Which functions sit behind which guard is today a list someone keeps;
with `PL-0GJC`'s type it is every function annotated with it, which
`typing.get_type_hints` finds.

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

**Done when.** The owner has chosen between the two, and the chosen one checks
the property above for every guard, finding the guards and what they protect
rather than listing them, so a new range is covered without editing the test.
