---
id: PL-H57W
title: Since PL-CZXN no check measures whether a branch that changes no core function weakens a core unit test, because PL-7FPD's route compares only the display modules' mutants; the same comparison over core's mutants took 538 to 968 s for one changed test file
priority: P1
effort: L
status: done
classes: defect, safety
milestone: v0.6.8
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py, docs/mutation-testing.md
blocked-by: PL-7FPD
added: 2026-10-24
closed: 2026-10-25
pr: 1807
payoff: a branch that loosens a core unit test, such as a wider tolerance on a concentration, is refused before it merges, as a loosened display test already is
verify: grep -q 'def test_a_branch_that_weakens_a_core_test_is_refused' tests/unit/test_diff_mutation.py
reenters: PL-CZXN
---

**Problem.** Since PL-CZXN no check measures whether a branch that changes no core function weakens a core unit test, because PL-7FPD's route compares only the display modules' mutants; the same comparison over core's mutants took 538 to 968 s for one changed test file

Split from `PL-7FPD` while triaging it on 2026-10-24. `PL-7FPD`'s problem covers any simulator test changed on a branch that changes no mutated function. The owner's answer, relayed by the coordinator, brings back a check for tests of what the interface displays, and `PL-7FPD`'s recommended route compares only the mutants of the `app/` display modules, because that cut one measured run from 1,837 mutants to 202. A core unit test loosened on a branch that changes no core function, such as a wider tolerance on a concentration, therefore stays unmeasured. That is the safety-critical standard's concern as much as a display test is. `PL-7FPD`'s brief holds the three measured runs: 538 s for every mutant `tests/unit/test_formatting.py` reaches, 968 s for every mutant two changed dashboard tests reach, and 113 s for the `app/` mutants of the same two tests, on four shared cores.

**Why it matters.** A core unit test is where a concentration, a dose or a unit is pinned. A branch that widens such a tolerance while changing no core function passes every check today, with a note naming the test file. The safety-critical standard in `CLAUDE.md` treats a wrong clinical value as a correctness failure, so a test that no longer catches one is the same concern as a display test, which the owner has just chosen to measure (`PL-7FPD`).

**Decision needed.** Should `docket verify` also compare mutants for a changed core unit test on a branch that changes no core function, at a measured cost of 538 to 968 s for every mutant such a test reaches?

**Recommendation: yes, scoped the way `PL-7FPD` scoped the display half.** Compare only the mutants in the core modules the changed test file imports by name, rather than every mutant the test reaches through building a run. `PL-7FPD`'s display cut took one run from 1,837 mutants to 202, and the same cut should bring this one near its 113 s figure. Measure the scoped cost on the two test files already timed before building it. Build it after `PL-7FPD`, because it reuses that item's comparison of base and branch mutants.

**Why it is the owner's call.** It reaches the safety-critical standard, and it reopens the cost side of the owner's 2026-10-19 ratified decision on `PL-CZXN`, which accepted leaving these tests unmeasured.

**Answered 2026-10-24: yes, scoped as recommended** (project owner, 2026-10-24, ratified, over leaving core unit tests unmeasured as `PL-CZXN`'s 2026-10-19 decision did, and over comparing every mutant a changed test reaches). The comparison covers only the mutants in the core modules that the changed test file imports by name. Its scoped cost is measured on `tests/unit/test_formatting.py` and the two `#1572` dashboard tests before it is built, and it is built after `PL-7FPD`, whose comparison of base and branch mutants it reuses.

**Done when.** `docket verify` refuses a branch that changes a core unit test so that a mutant in a core module the test imports by name, which the test's base version kills, survives the branch's version. It passes a branch whose changed test still kills every such mutant. `tests/unit/test_diff_mutation.py` has `test_a_branch_that_weakens_a_core_test_is_refused`, and the brief records the scoped cost measured on the files named above.

**Measured 2026-10-25, before building, on four cores that no other session shared** (load average about 4.5, from this session's own runs). Each run selected only the named tests, in a copy of the tree, as `compare_tests` does for the base version.

| Tests | Mutants run | Mutants the tests reached | Time |
| --- | --- | --- | ---: |
| all of `tests/unit/test_formatting.py` | the `app/` modules and the 5 `core/` modules it imports | 862 | 219 s |
| the same | every mutant | 1,893 | 493 s |
| the two tests `#1572` changed in `tests/unit/test_dashboard_frame.py` | the `app/` modules and the 8 `core/` modules the file imports | 1,386 | 325 s |
| the same | every mutant | 1,962 | 415 s |

So scoping by import cuts the base run by 55% for `test_formatting.py` and by 22% for the dashboard tests, whose file imports 8 of the 21 files under `core/`, all of which mutmut mutates. The branch run takes only the mutants the base run caught, so it costs less than the base run. A changed core test therefore adds about two to four minutes to each version of its file, on top of the display comparison's two. That is the cost the owner accepted on 2026-10-24.

**What was done.** `tools/diff_mutation.py` has `core_imports`, which lists the modules under `anesthesia_sim.core` that a test file names in `from anesthesia_sim.core.x import ...`, `from anesthesia_sim.core import x` or `import anesthesia_sim.core.x`, inside a function or not. `compare_tests` takes the union of those modules over the base and branch versions of each compared file, keeps the ones mutmut mutates, and runs their mutants beside the display modules' in both runs. Each module's pattern takes only its own functions' mutants, so a file that imports from the package `anesthesia_sim.core` itself does not bring in every submodule. A mutant that the base version kills and the branch's version misses refuses the branch as a display mutant does. `tests/unit/test_diff_mutation.py` has `test_a_branch_that_weakens_a_core_test_is_refused`, its passing counterpart, and a test of `core_imports`. `docs/mutation-testing.md` says what the check now reads and what stays unmeasured: a fault the test catches only through a `core/` module it does not import by name.

**Measured end to end on 2026-10-25.** A message was added to the second assertion of `tests/unit/test_concentration.py::test_the_two_forms_convert_both_ways`, which keeps every assertion, and `tools/diff_mutation.py --verdict` was run against `origin/main`. The base version of that test caught 10 mutants of `app/` and of the 7 `core/` modules the file imports, the branch's version still caught all 10, and the verdict passed in 133 s for both runs. A second run, with a message added to the last assertion of `tests/unit/test_dashboard_frame.py::test_a_run_statement_carries_the_locks_and_the_banner_it_is_given`, compared 497 mutants of `app/`, of the `anesthesia_sim.core` package and of the 8 `core/` modules the file imports, all still caught, and took 911 s for both runs. `PL-7FPD`'s display-only run of the same kind took 197 s on 60 mutants. Most of the time is the branch run, which takes the whole changed file. So a changed dashboard test now costs about 15 minutes, for both versions together, which is inside the 538 to 968 s for each version that the owner accepted on 2026-10-24. The refusing direction is covered by `test_a_branch_that_weakens_a_core_test_is_refused`, which stubs mutmut, because this session's permission check refused the edit that deletes a real assertion.

**Generator check.** An instance of `PL-4W2L`'s fact, "whether a branch's diff weakens its tests", reached through `PL-CZXN`, which closed on 2026-10-24, like `PL-7FPD`. Recorded as `reenters: PL-CZXN`.

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still true.** `PL-7FPD`, which this waited on, is done. `tools/diff_mutation.py` still compares only the display modules' mutants, and its own comment says a test of `core/` on a branch that changes no `core/` function stays unmeasured. The named test does not exist.
