---
id: PL-TN0G
title: Nothing flags a test assertion that never decides a result: mutation testing asks whether some assertion catches each fault, never whether each assertion catches a fault the others miss, so the step-size test's 0.5% limit sat beside a stricter 1e-14 limit from #376 (2026-09-05) until a prose rewrite found it (PL-VXM0). Add a warning that switches off each assertion of a changed simulator test in turn and names any whose removal loses no caught mutant, and run it once over the existing unit and reference tests
priority: P2
effort: M
status: done
classes: feature, infra
feature: dead-test-limits
milestone: v0.6.15
touches: .claude/rules/dead-ends-apparatus.md, .claude/rules/test-oracles.md
deferred-from: v0.7.0 - workflow tooling outside the schematic release, waiting on the owner's answer
added: 2026-11-03
closed: 2026-11-03
pr: 1969
payoff: a test limit that another assertion always overrules is named at review, so no displayed explanation is written for a number that never decides anything
verify: grep -q 'One ordinary run that pairs two limits' .claude/rules/dead-ends-apparatus.md && grep -q 'Say what kind of limit each chosen tolerance is' .claude/rules/test-oracles.md && ! grep -q 'assertion_notes' tools/diff_mutation.py
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

**Progress, 2026-11-03 (session reset for length, not for the work).**

Built and pushed on `claude/pl-tn0g-dead-assertion-warning` (draft #1969):

- `tools/assertion_probe.py` (the rewrite, the pytest plugin, the verdicts, the
  driver, `--sweep`, `--report`), with `tests/unit/test_assertion_probe.py`.
  The tests pin a never-deciding pair, a deciding pair, a raised run left out,
  parametrized cases counted together, and the plugin end to end.
- `diff_mutation.compare_tests` called `assertion_notes`, which probed the
  unit tests `branch_selection` names and added a note for each. The mutant
  generation was shared as `GENERATE_SCRIPT`. Both were removed on 2026-11-03,
  under answer (a) below.
- A section of `docs/mutation-testing.md` headed "Assertions that never decide
  a result" said how it worked. It was removed on 2026-11-03 with the note.
- Two choices made while building. A `with pytest.raises(...)` block is
  rewritten too (`__probe_raises__`), so its failures count as an assertion's
  rather than as a raise. pytest runs with `--tb=native`, because pytest's own
  traceback took 185 ms of a 190 ms mutant run.

Running in the background, in this session's scratchpad
(`/tmp/claude-0/-home-user-open-anesthesia-sim/6dbe0110-85af-5e82-a8e7-345cdd45c5e6/scratchpad`):

- The positive control: `control-out/` holds the probe of
  `test_step_refinement_converges` on a worktree of `334d9cc6` at
  `scratchpad/control`, 1,812 mutants at about 2 s each. Its report goes to
  `control-out/report.txt`.
- The unit sweep: `sweep-unit/`, three processes, `--budget 900`, over the 60
  simulator unit test files in `sweep_files.txt`. Report in
  `sweep-unit/report.txt`.
- Still to run: the 14 reference files, with a per-case budget, naming what it
  leaves out. Remove the worktree with `git worktree remove` when done.

Early step-7 evidence, from the smoke run of `tests/unit/test_alveolar.py`: it
named 10 assertions, and none is a dead limit. Each is one guard reached by
several routes (a `replace`, a `copy` and a `pickle` of the same compartment,
lines 213-222), or two checks of one value that every mutant breaks together
(lines 348 and 352). Three of them are strict subsumption (line 188 by 185, and
213 and 219 by 222), so the strict filter alone does not separate a dead limit
from these. If the sweep agrees, the per-branch note should be cut to what the
`PL-VXM0` pattern needs, or dropped, and that choice recorded here.

**Positive control, 2026-11-03: the probe does not name the 0.5% limit.** On a
worktree of `334d9cc6`, `test_step_refinement_converges` ran under its 1,812
reachable mutants in 14 minutes: 828 runs completed and 984 raised. Neither of
its two assertions failed in any completed run, so both are counted as failing
for no mutant, and nothing is named. No mutant made the result depend on the
step size, because each one changes all three step sizes alike. The 0.5% limit
was dead by logic rather than by mutants. It passes whenever each gap is within
its absolute tolerance of 1e-8, and the other assertion already requires every
gap to be within 1e-14 (`STEP_REFINEMENT_ABSOLUTE_TOLERANCE` and
`STEP_REFINEMENT_SETTLED_GAP` at `334d9cc6`). A mutant can show that one
assertion overrules another only when some mutant breaks what they check, and
here none does.

**Decision asked, 2026-11-03.** Does the warning at review still get built?
Recommendation (session, 2026-11-03): no. The mutation approach cannot see the
case that motivated it. On `tests/unit/test_alveolar.py` its 10 warnings were
all false alarms: one guard reached by several routes, or two checks of one
value. So the plan is:

1. Remove the per-branch note from `diff_mutation.compare_tests`.
2. Finish the unit sweep, and record its counts in `### The first sweep`.
3. Keep `tools/assertion_probe.py` only if the sweep names at least one real
   dead limit. Otherwise remove it.
4. Record the approach in `docs/dead-ends.md`, with this control as the reason.

What found the 0.5% limit was the question "why is this number this value",
which `.claude/rules/plain-writing.md` § "Give a chosen value its reason from a
record" now asks of every chosen value a document states. The other route is a
check that one assertion's limit implies another's. That would read the test's
own comparisons, which is judgment, and it would be a new item.

**Answer** (project owner, 2026-11-03, ratified, over building the warning
at review): no, on the mutation approach.

**The unit sweep, finished 2026-11-03.** It ran 52 minutes over 146 tests with
two or more assertions. Of 546 assertions, 206 decide a result, 199 never
decide, and 141 fail for no mutant. There were 71,071 completed runs, 62,837
raised runs and 16 timeouts. Three test cases were left out: two stopped
before they finished, and in one a mutant left state behind. One of the three
processes was killed for memory at about 1.4 GB, so its files were swept only
in part. Of the 199 named assertions, 71 are looser than one other assertion
and 109 catch exactly the same mutants as another. Nearly all are in three
files: `tests/unit/test_dashboard_frame.py` (106),
`tests/unit/test_formatting.py` (67) and `tests/unit/test_run_definition.py`
(26).

None is a dead limit. Every named assertion that compares a number was read.
Most check one value two ways, or several inputs of one formatter. One is
implied by its neighbour: `tests/unit/test_formatting.py:689`,
`abs(centre - 2.17) <= 0.25`, always passes when line 682's
`centre == pytest.approx(2.16)` does. It is deliberate: it compares the centre
with Song et al.'s published mean and standard deviation, which checks the
expected value 2.16 independently, and its comment gives the reason for 0.25.
The sweep's raw output was in the session scratchpad and goes with it.

**Reopened by the owner, 2026-11-03.** The owner asked whether dropping the
tool means not worrying about dead limits at all. Nothing else would catch the
next one. Only `.claude/rules/plain-writing.md` § "Give a chosen value its
reason from a record" asks why a limit is its value, and it covers only values
a document states; no rule under `.claude/rules/` asks it of a test tolerance
that no document quotes. A static check comparing two limits would not have
caught the 0.5% case either: at `334d9cc6`, lines 397-415 of
`tests/reference/test_sevo_patient.py`, one assertion compares each pair with
`pytest.approx` and the other builds the same coarse-minus-fine differences
in a list and takes `max()`, so seeing that they test one thing takes
reasoning (inferred from the code).

**Decision asked, 2026-11-03.** Which of three routes?

- **(a)** Drop mutation. Change `tools/assertion_probe.py` to record, in one
  ordinary test run, the value each comparison got and the limit it allowed,
  and list any limit orders of magnitude looser than the tightest one in the
  same test. Add a rule to `.claude/rules/test-oracles.md` that a test
  tolerance carries its reason in a comment.
- **(b)** Drop mutation and the tool, and add only the tolerance-reason rule.
- **(c)** Drop mutation and the tool, and add nothing.

**Recommended** (session, 2026-11-03): **(a)**. At `334d9cc6` the test's
docstring gives the mixed-venous gap as about 4e-17. The 0.5% check allowed at
least 1e-8, about 10^8 times that gap, and the 1e-14 check about 250 times, so
the report should name the 0.5% limit (inferred, not yet run). It costs one
test run, not 52 minutes of mutants. Stopping rule, set in advance: run the
one test at `334d9cc6` first, and drop the report if it does not name the 0.5%
limit. Then sweep, and drop it if its list holds no real dead limit. Under
every answer the per-branch note in `tools/diff_mutation.py`, its
`docs/mutation-testing.md` section and the mutation runs go, and the approach
is recorded in `.claude/rules/dead-ends-apparatus.md` § "Mutation testing"
(already written).

**Answer: (a)** (project owner, 2026-11-03, ratified, over (b) the rule alone
and (c) nothing). The owner also asked for the best practice to be researched.

**Research, 2026-11-03.** Verified means the page itself was read; the rest
comes from search-result excerpts, because par.nsf.gov, osti.gov,
errorprone.info and export.arxiv.org do not resolve from this container.

- Octopus, merge request !3, "Update to testsuite tolerances by systematically
  reducing them", 2016,
  https://gitlab.com/octopus-code/octopus/-/merge_requests/3 (verified). A
  default tolerance left "many tests having a much larger tolerance than the
  minimum one required", so "large changes in the values calculated by the
  code will not be detected". The fix is one tolerance per check, reduced to
  the minimum that passes on every build machine. Writing each spread in the
  test lets "a script ... automatically identify all the tests that have
  unusually high spreads". It also warns that results which vary across
  machines need large tolerances, which "can hide further problems".
- Dutta, Shi and Misailovic, "FLEX: Fixing Flaky Tests in Machine Learning
  Projects by Updating Assertion Bounds", ESEC/FSE 2021,
  https://github.com/uiuc-arc/flex (authors and venue verified from the
  README). It picks a bound from many repeated runs with extreme value theory.
  Excerpt only: 35 flaky tests from 21 projects.
- Xia, Dutta and others, "Balancing Effectiveness and Flakiness of
  Non-Deterministic Machine Learning Tests" (FASER), ICSE 2023,
  https://github.com/ise-uiuc/FASER (title and venue verified). Excerpt only:
  it trades fault detection, measured by mutation score, against the chance
  of a flaky failure, and tightened the bounds of 23 of 87 tests, raising
  their mutation score by 15.76 percentage points on average.
- Error Prone, FloatingPointAssertionWithinEpsilon,
  https://raw.githubusercontent.com/google/error-prone/master/docs/bugpattern/FloatingPointAssertionWithinEpsilon.md
  (verified). It flags a tolerance smaller than the gap to the next
  representable number, which makes the check an exact equality in disguise.
- Jahangirova, Clark, Harman and Tonella, "Test oracle assessment and
  improvement", ISSTA 2016, pp. 247-258, https://doi.org/10.1145/2931037.2931062
  (excerpt). Mutation finds an assertion too weak to catch a fault; generated
  inputs find one too strict for correct behaviour.
- Schuler and Zeller, "Checked coverage: an indicator for oracle quality",
  Software Testing, Verification and Reliability 23(7):531-551, 2013
  (excerpt). It counts the statements whose results reach an assertion.
- Kanewala and Bieman, "Testing scientific software: a systematic literature
  review", Information and Software Technology, 2014,
  https://doi.org/10.1016/j.infsof.2014.05.006 (excerpt). The missing oracle
  is the main difficulty in testing scientific code.
- A Sandia report, https://www.osti.gov/servlets/purl/1709044 (excerpt only;
  title and authors unread). It separates acceptance criteria for verifying a
  numerical algorithm, taken from its known mathematical properties, from
  criteria for its adequacy, taken from what the application needs.
  Oberkampf and Roy, *Verification and Validation in Scientific Computing*,
  Cambridge University Press, 2010, chapter 5, is the textbook form.

**What the research changes in the build.**

1. No published tool was found that names an assertion implied by another.
   The nearest practice tightens each bound toward the observed spread
   (Octopus, FLEX, FASER). This simulator is deterministic, so its spread
   across runs is zero, and the observed size is the deviation in one run.
2. A raw ratio of allowed to observed deviation would flag nearly every bare
   `pytest.approx`, whose default relative tolerance of 1e-6 is about 10^9
   times the rounding error of exact arithmetic. A report that fires on all
   of them is read past. So compare limits only where two assertions in one
   test recorded the same nonzero number. Then one limit implies the other by
   arithmetic, and units cancel. In the 0.5% case the deviation that
   `pytest.approx` computes, |coarse - fine|, and one entry of `gaps` should
   be the same float, because floating-point subtraction gives the same
   magnitude either way round (inferred; the control checks it).
3. The report names a pair and a person decides. It never tightens a limit to
   the observed value, because results drift across machines and library
   versions (Octopus).
4. The tolerance rule follows the Sandia split. Each chosen tolerance's
   comment says which kind it is and where its number comes from: a
   numerical limit, from the method's expected error or the rounding of the
   arithmetic, or a clinical or published limit, from a cited source. Line
   689 of `tests/unit/test_formatting.py` is the second kind, and its comment
   is what tells a reader the match is deliberate. A bare `pytest.approx` sets
   no chosen value and needs no comment.

**Next steps** (written 2026-11-03 for the session after the reset).

1. Keep the rewrite in `tools/assertion_probe.py` and drop its mutant runs.
   Insert `__probe_enter__('id') or` at the start of each `assert` test, so
   what is recorded while it runs belongs to that assertion. Wrap
   `pytest.approx`'s scalar comparison (check the class name in the installed
   pytest) to record the deviation and the allowed size, max(rel x
   |expected|, abs). Rewrite a single comparison with a numeric side,
   `L <= R` and the like, to `__bound__('id', L, '<=', R)`. Count and name
   the forms it does not read: `math.isclose`, chained comparisons and
   assertion helpers.
2. Run the positive control first: `test_step_refinement_converges` at
   `334d9cc6`, in a worktree. It must name the `pytest.approx` limit as looser
   than the 1e-14 limit on the same gap. If it does not, stop, and drop the
   report.
3. Sweep `tests/unit` and `tests/reference`, one ordinary run each, and read
   every named pair. Keep the report only if it names a real dead limit
   beyond the control. Otherwise drop it and add it to the dead end in
   `.claude/rules/dead-ends-apparatus.md` § "Mutation testing".
4. Under either outcome: remove `assertion_notes` from
   `diff_mutation.compare_tests` with its two tests and the mutant-map code
   only it uses, remove the `docs/mutation-testing.md` section, add the
   tolerance rule (step 4 above) to `.claude/rules/test-oracles.md` citing
   `PL-TN0G`, and record the counts here. If the report is kept, decide
   where its per-branch note runs: one ordinary run of the changed tests.

**The limit sweep, finished 2026-11-03.** All four steps are done, and the
report is dropped.

1. The probe was rebuilt as step 1 says, with one change: each `assert` test
   became `__probe_exit__(__probe_enter__('id'), (cond))`, so a comparison made
   after the assertion ends is not charged to it. A bound's checked number was
   the left side, unless the left side was a literal or an upper-case
   constant and the right side was not. A number was paired only when it was
   finite, nonzero and not a whole number.
2. The positive control passed. At `334d9cc6` it named
   `tests/reference/test_sevo_patient.py:399` (the `pytest.approx` limit) as
   looser than `:411` (the 1e-14 limit). They shared 3 of the 6 numbers the
   looser limit checked, and the looser one left 1.14e8 to 1.67e9 times the
   room. So the deviation `pytest.approx` computes and the entry of `gaps` were
   the same float, as the research inferred (verified by this run).
3. The sweep ran 3,963 test cases of `tests/unit` and `tests/reference` in
   6 min 50 s on four workers, and all passed on the rewritten copy. They ran
   9,011 assertions, summed over cases, and 1,944 of those set a limit on a
   fractional number. 3,588 times, two assertions set the same limit on one
   number. It could not read 36 chained comparisons, 8 assertion helpers
   called as statements, and 3 `isclose` calls. It named six pairs, and none
   is a dead limit:
   - `tests/reference/test_canonical_evaluation.py`, lines 506 and 511: a
     fraction and an accumulator with the same rounding error, 4.4e-16.
   - `tests/unit/test_layout_model.py`, lines 219 and 997: a rectangle's
     coordinate and the gap between two edges, at 5.6e-17.
   - `tests/unit/test_numerical_envelope_sweep.py`, lines 313 and 534: the
     agent balance of the whole system and of the circuit stepped alone. They
     shared 31 rounding residues, at limits of about 3 and 4 machine epsilons.
     Each guards its own code path.
   - The same file, lines 305 and 485: two ceilings on fractions held at a
     99% dial, equal to three significant figures, in different loops.
   - `tests/reference/test_sevo_patient.py`, lines 510 and 518: the last
     washout step against the step before, and the same amount against the
     loaded amount. The second exists so the run cannot pass by never washing
     out.
   - `tests/unit/test_agent_simulation_validation.py`, lines 614 and 615: an
     absolute and a relative error that the test makes equal by delivering
     1 L, so that it checks both branches of the validator.
4. Under that outcome the probe, its tests, its tools-map entry and its
   `workflow_paths` entry are removed, and the attempt is a second entry in
   `.claude/rules/dead-ends-apparatus.md` § "Mutation testing". The mutation
   note and its documentation section are removed, as the answer above says.
   `.claude/rules/test-oracles.md` gains rule 7, which asks each chosen
   tolerance to say whether it is a numerical or a clinical or published
   limit and where its number comes from, and to check for an overlapping
   limit before adding a second one.

The rounding-level matches are why the report could not stand on its own.
Rounding errors are small multiples of a power of two, so two unrelated
quantities often share one. A filter for that would have to tell a shared
quantity from a shared value, which is the judgment the report was meant to
spare. `PL-NYFZ` (a tolerance below the gap between neighbouring
floating-point numbers) is a different check and stays open.
