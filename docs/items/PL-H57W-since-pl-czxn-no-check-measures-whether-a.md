---
id: PL-H57W
title: Since PL-CZXN no check measures whether a branch that changes no core function weakens a core unit test, because PL-7FPD's route compares only the display modules' mutants; the same comparison over core's mutants took 538 to 968 s for one changed test file
priority: P1
effort: L
status: blocked
classes: defect, safety
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py, pyproject.toml
blocked-by: PL-7FPD
added: 2026-10-24
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

**Generator check.** An instance of `PL-4W2L`'s fact, "whether a branch's diff weakens its tests", reached through `PL-CZXN`, which closed on 2026-10-24, like `PL-7FPD`. Recorded as `reenters: PL-CZXN`.
