---
id: PL-TN0G
title: Nothing flags a test assertion that never decides a result: mutation testing asks whether some assertion catches each fault, never whether each assertion catches a fault the others miss, so the step-size test's 0.5% limit sat beside a stricter 1e-14 limit from #376 (2026-09-05) until a prose rewrite found it (PL-VXM0). Add a warning that switches off each assertion of a changed simulator test in turn and names any whose removal loses no caught mutant, and run it once over the existing unit and reference tests
priority: P2
effort: M
status: ready
classes: feature, infra
feature: dead-test-limits
touches: tools/diff_mutation.py, tools/assertion_probe.py, tests/unit/test_diff_mutation.py, tests/unit/test_assertion_probe.py, docs/mutation-testing.md, docs/apparatus.md, docket.toml
added: 2026-11-03
payoff: a test limit that another assertion always overrules is named at review, so no displayed explanation is written for a number that never decides anything
verify: grep -q 'never decides' tools/assertion_probe.py && grep -q 'assertion_probe' tools/diff_mutation.py && grep -q 'Assertions that never decide a result' docs/mutation-testing.md && grep -q '### The first sweep' docs/mutation-testing.md
---

**Problem.** Nothing flags a test assertion that never decides a result: mutation testing asks whether some assertion catches each fault, never whether each assertion catches a fault the others miss, so the step-size test's 0.5% limit sat beside a stricter 1e-14 limit from #376 (2026-09-05) until a prose rewrite found it (PL-VXM0). Add a warning that switches off each assertion of a changed simulator test in turn and names any whose removal loses no caught mutant, and run it once over the existing unit and reference tests

**Why it matters.** A test limit that never decides a result still has to be
explained to every reader of `docs/MODEL.md`, and it can hide a looser bound
than the reader assumes. The owner rejected five explanations of one such
limit on 2026-11-02 (`PL-VXM0`). Mutation testing as run here asks only whether
some assertion catches each mutant, so it cannot find a limit like that one.

**Generator check.** A one-off, and work the owner asked for on 2026-11-03.
The fact misread is whether one assertion's failures are ever the only
failures in its test, and no tool records it. `bin/docket generators --misread`
names no head with that fact. One instance is known, `PL-VXM0`.

**Design** (session decision, 2026-11-03; the build follows it).

1. **One run per mutant and test, not one per assertion.** Rewrite each
   assertion in a copy of the test files so that it records a failure and
   carries on. An `assert cond, msg` becomes `assert __probe__("path:line:col",
   (cond)), msg`. A call statement whose function name starts with `assert`,
   such as `np.testing.assert_allclose(...)`, becomes `__probe_call__("id",
   lambda: <call>)`. Both inserts keep every line number. Check that the
   rewritten file compiles, and name any file that does not. One run of a
   test under a mutant then gives the set of assertions that failed. That set,
   for every mutant, is the kill matrix with assertions as rows. It answers
   "does removing assertion A alone lose a caught mutant" for every A at once.
   Kurtz, Ammann, Delamaro, Offutt and Deng, "Mutant subsumption graphs",
   ICST Workshops 2014, pp. 176-185, define the same matrix with tests as rows.
2. **In one pytest process per test file, switching mutants in place.**
   mutmut's trampolines read the active mutant at each call
   (`mutmut.mutation.trampoline.set_mutant_under_test`), so a plugin can loop
   over mutants without starting a process for each. Generate the mutants the
   way `LIST_SCRIPT` in `tools/diff_mutation.py` does. For each test item:
   - run it under the mutant name `stats` to record which mutated functions it
     reaches;
   - run it with no mutant, and skip it with a note unless it passes;
   - run it under each mutant of the functions it reached, with
     `runtestprotocol(item, nextitem=None)`, so fixtures are set up again;
   - run it with no mutant again at the end, and mark its results unreliable
     if that run fails, because a mutant left state behind.
   Set a time limit on each run with `signal.setitimer`, raising a
   `BaseException` subclass, at about ten times the clean run plus 2 s. Write
   each result as a JSON line as it finishes, so a crash keeps what was done.
3. **The verdict per assertion, from the matrix, in tests with two or more
   assertions.** A mutant counts only where the run completed. A run that
   raised outside an assertion is excluded and counted, because the
   assertions after the raise were never evaluated.
   - *Decides*: some mutant fails A and no other assertion in the test.
   - *Never decides* (the warning): A fails for at least one mutant, and every
     one of those mutants also fails another assertion in the same test. Name
     the assertions that cover it, and say whether one of them covers all of
     A's mutants alone and catches more, which is the `PL-VXM0` pattern.
   - *Fails for no mutant*: counted per file, not named. Removing it also
     loses no caught mutant, but mutants cannot reach what it guards. mutmut
     never changes the data files or the constants, so most of these protect
     values that mutants cannot test. Naming them would bury the warning.
4. **Wiring.** Put the probe in a new `tools/assertion_probe.py`, with the
   plugin and the driver, and call it from `compare_tests` in the branch copy
   after mutmut's run there, for the tests that `branch_selection` names. Each
   assertion that never decides becomes a note in the `--verdict` JSON, so
   `bin/docket verify` prints it and refuses nothing.
5. **The one-time sweep**, `python3 tools/assertion_probe.py --sweep`, over
   the simulator unit test files and `tests/reference/`. Run it with the Bash
   tool's `run_in_background`, split across four processes by file. Record the
   counts and the named assertions in a new section of `docs/mutation-testing.md` headed Assertions
   that never decide a result, and file an item for each one that is a real
   dead limit. The reference suite took more than 6 minutes on four cores on
   2026-11-03 (in this session's scratchpad `ref.log`; re-time it with
   `--durations=15`). So the sweep takes each reference test whose clean run is
   short enough for a budget the session sets, and names the rest as not
   measured.
6. **Positive control.** On a tree that still holds
   `STEP_REFINEMENT_RELATIVE_TOLERANCE`, the sweep must name the 0.5% assertion
   in `test_step_refinement_converges` as never deciding, covered by the 1e-14
   assertion. If it does not, the probe is wrong. Run this before `PL-VXM0`
   removes that assertion, or on a checkout of `334d9cc6`.
7. **Then decide whether the per-branch warning earns its place.** Count how
   many named assertions in the sweep are real dead limits and how many are
   two assertions that the mutants happen to break together, such as two
   concentrations of one run. If most are the second kind, keep only the
   strict case: one other assertion catches every mutant A catches, and more.
   Record the count and the choice here.

Known limits to state in the documentation. The test modules are imported once,
with no mutant applied. So an expected value computed at import time from
simulator code is the unmutated one, which credits an assertion with a kill
that a real fault might not give. That is the false kill described in
`docs/mutation-testing.md` § "Pitfalls", and it errs toward fewer warnings. A
`with pytest.raises(...)` block is not rewritten, so its failure counts as an
exception.

**Done when.** `tools/assertion_probe.py` builds the kill matrix for a test
file and prints each assertion that never decides, with the assertions that
cover it, and its tests pin a never-deciding pair, a deciding pair, and a
mutant that raises. `--verdict` carries those assertions as notes for changed
tests. The sweep has run, the positive control is named, and
a new section of `docs/mutation-testing.md` headed Assertions that never decide a result, records
the counts and the step-7 choice.
