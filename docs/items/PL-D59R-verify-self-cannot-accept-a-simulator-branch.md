---
id: PL-D59R
title: verify --self cannot accept a simulator branch that changes a large display unit test: tools/diff_mutation.py's weakened-test comparison runs each display mutant its base version catches against the branch's whole changed unit-test files, which took 66 minutes for the base half on PL-ZR49 and projected about four hours for the branch half, past the audit's 2-hour bound
priority: P1
effort: M
status: ready
classes: defect, perf
touches: tools/diff_mutation.py, tests/unit/test_diff_mutation.py, .claude/skills/docket/modes/close-out.md, docs/mutation-testing.md
deferred-from: v0.7.0 - captured after the freeze; a close-out audit cost in the workflow lane, not safety or science, which its band ranks rather than the gate
added: 2026-10-26
payoff: a simulator branch that changes a large test file can finish close-out's mutation audit, instead of spending hours on a check that can only refuse
verify: ! grep -qF 'That costs about two more' .claude/skills/docket/modes/close-out.md
not-delegable: only a verify --self run reaching a verdict within its 2-hour bound on a branch like PL-ZR49's proves the fix, and only a session can run one
---

**Problem.** verify --self cannot accept a simulator branch that changes a large display unit test: tools/diff_mutation.py's weakened-test comparison runs each display mutant its base version catches against the branch's whole changed unit-test files, which took 66 minutes for the base half on PL-ZR49 and projected about four hours for the branch half, past the audit's 2-hour bound

**Evidence.** Measured on 2026-10-26 by `PL-ZR49`'s close-out, `bin/docket verify --self` on `claude/pl-zr49-iusum9` at `ded828cb`. The branch changes four unit-test files that import the simulator: `tests/unit/test_dashboard_frame.py`, `test_bookmarks.py`, `test_run_definition.py` and `test_display_units.py`.

- The changed-line mutation run took six minutes (12:30 to 12:36 UTC). It caught all 41 mutants.
- `compare_tests` then ran the base versions in a scratch copy, `/tmp/diff_mutation_<random>/base`. Its mutmut log ran from 12:37 to 13:43 UTC, 66 minutes.
- The branch half started at 13:45 with 4,458 mutants, the ones the base half caught. At 13:59 it had run 264, about 19 a minute, with 255 caught, 9 timed out and none surviving. At that rate the 4,458 mutants need about four hours.
- `MUTATION_TIMEOUT_S` in `subprojects/docket/src/docket/verify.py` is 7,200 s. So the mutation check can only answer "no answer", and `verify` refuses. The run was stopped at 14:00 by the session's own 90-minute limit, and a second run was stopped by hand once the arithmetic showed it could not finish.

The branch half runs each mutant against the branch's version of every changed unit-test file, whole (`compare_tests`'s docstring). `test_dashboard_frame.py` is large, so each mutant costs seconds. Close-out step 5 estimates this check at "about two more minutes for each version of the changed tests". That holds for a small test file and not for this one.

**Why it matters.** Close-out step 5 asks a session to re-run the audit until it prints `ACCEPT`. A simulator branch that changes a large display unit test cannot get there, so the session either spends hours or reports a refusal that says nothing about the branch. Of the 87 merges to `main` since 2026-09-26 that changed `src/anesthesia_sim/app/`, 26 also changed `test_dashboard_frame.py` (`git log --first-parent`, counted 2026-10-26).

**Done when.** `verify --self` gives an answer on a branch like `PL-ZR49`'s within its bound. That could come from running the branch half on the changed test ids rather than the whole files, from narrowing the mutants to those the changed tests reach, or from a bound per file that reports what it did not measure as a note. Close-out step 5's cost estimate states the measured cost.

**Seen again, 2026-10-26.** Pull request #1864 (`PL-0WFJ` and seven other core findings, from a Projects thread) reports the same outcome in its body: its `bin/docket verify --self` "stopped at the 2-hour limit before it printed a verdict". That branch changes core modules and their unit tests rather than a display test, so the cost is not limited to `test_dashboard_frame.py`.

**Generator check.** A one-off. The fact misread is what the mutation audit costs on a branch. Close-out step 5 sized it on a small test file, and the cost grows with the size of each changed test file. No head's `misread:` states it.

**Progress, 2026-10-31.** The cost came from the selection, not from the branch run alone. `base_selection` fell back to the whole file whenever any line outside a test changed, such as an import, a helper or a constant. Over the 247 changed simulator unit-test files in the 200 merges before 2026-10-31, that happened for 187. Each mutant re-imports its test files, because `[tool.mutmut]` runs `forkserver` with no warm-up. It then runs every selected test that reaches it, and a timeout costs 30 times those tests' summed duration (mutmut 3.8.0's `timeout_multiplier` of 15, doubled). So the number of selected tests sets the cost of both runs.

The fix, on `claude/pl-d59r-mutation-check-1vgzei`:

- `changed_tests` in `tools/diff_mutation.py` compares each test's syntax tree, and that of every module-level name it reaches, between the two versions. A changed helper selects only the tests that reach it. A docstring, a comment, a new import or a new helper selects none. Over the same 247 files, 2 fall back to the whole file. The 11 tests the new rule drops all had docstring-only changes. A per-test coverage run of the changed files of `PL-ZR49`'s merge (`40a442ee`) and #1864 (`adc93274`), on both sides, found no test that executes a changed line and is not selected.
- The branch run tries the base-caught mutants against the branch's changed and added tests first (`branch_selection`), and runs only the ones those miss against the whole files.

On `PL-ZR49`'s merge the selections drop from two whole files to 59 of `test_dashboard_frame.py`'s 161 tests and none of `test_run_definition.py`'s. On #1864, six whole-file fallbacks drop to between 0 and 4 tests each.

Still to do: measure `diff_mutation.py --verdict` on `40a442ee` against `40a442ee^`, and on `adc93274` against its parent, with this branch's `tools/` overlaid in a worktree. Then write the measured cost into close-out step 5 and into `docs/mutation-testing.md`.
