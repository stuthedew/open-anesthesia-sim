---
id: PL-3JG7
title: At least 32 of the 118 red runs since 2026-09-21 that caught a real defect failed a check a local make check also runs: 18 whole-repository self-check tests in pytest, which the push guard does not run, and 14 repeated pushes on three branches past a failure make check reports
priority: P2
effort: S
status: ready
classes: infra
feature: fewer-red-runs
touches: .claude/hooks/push-check-guard.sh, tests/unit/test_push_check_guard.py
added: 2026-10-25
payoff: a push that a local make check would refuse for a misplaced apparatus file, a malformed fixture id, an inert type: ignore or a line-split rule is refused in the session, before it spends a red run
verify: grep -q 'def test_a_push_whose_project_interpreter_check_fails_is_refused' tests/unit/test_push_check_guard.py
---

**Problem.** At least 32 of the 118 red runs since 2026-09-21 that caught a real defect failed a check a local make check also runs: 18 whole-repository self-check tests in pytest, which the push guard does not run, and 14 repeated pushes on three branches past a failure make check reports

**Measured 2026-10-25 by `PL-2D1S`**, which read the log of every red run on
the pull requests of items closed in ISO weeks 39 to 43. Two groups failed a
check that a local `make check` runs too:

- **18 runs**: a whole-repository self-check test under `tests/unit/` refused
  a file the branch itself had added. Eight were a new apparatus file missing
  from `docket.toml`'s `workflow_paths`
  (`test_workflow_paths_check.py::test_this_repository_passes_its_own_check`),
  five a malformed id in a test fixture
  (`test_fixture_id_check.py::test_the_repository_carries_no_malformed_id`),
  three a `splitlines` or text-mode rule (`test_line_splits.py`), and two a
  stale citation. The push guard, `.claude/hooks/push-check-guard.sh`, runs
  `doc_check`, `branch_id_check` and `bin/docket check --verify`, and none of
  these tests. Example: run 36808581552, where
  `tests/unit/test_quality_step_order.py` was not in `workflow_paths`.
- **14 runs**: three branches pushed again and again past a failure that
  `make check` also reports. `r417-link-24` failed seven times on unresolved
  test imports, and its fix commit `2feb889d` says local `make check` stopped
  there too. Example: run 38094131155.

**The question.** Whether the self-check tests are fast enough to run in the
push guard beside `doc_check`, and what made three sessions push past a
failing local check. `PL-PLSJ` found the second mechanism in September, and
`PL-S1BG` added `bin/docket check --verify` to the guard for it.

**Why it matters.** Each of these red runs is a push and a full quality run
that a check on the session's own machine would have saved.

**Measured 2026-10-26, at triage.** `PL-2D1S`'s classification lists 32 defect
runs whose failing step is a check `make check` also runs: 17 in `pytest` and
15 in a `tools/` step. Four checks are behind 26 of the 32, and the push
guard runs none of them:

| Check | Runs | On a session branch | On a Projects thread |
| --- | --- | --- | --- |
| `tools/workflow_paths_check.py` (both self-check tests in `test_workflow_paths_check.py` call it) | 8 | 6 | 2 |
| `tools/ignore_check.py` (7 of them `r417-link-24`'s repeated pushes) | 9 | 9 | 0 |
| `tools/fixture_id_check.py` (the tool's own step and its self-check test) | 6 | 4 | 2 |
| `tests/unit/test_line_splits.py` | 3 | 3 | 0 |

A session branch is one where the guard runs. Projects threads run no
repository hooks (`PL-D1FD`), so no guard can catch the 4 thread runs above,
or the 2 `fact_home_check` runs that were also on a thread. That leaves 26
runs a guard could reach, and these four checks cover 22 of them. The other 4
were one run each: `possessive_section_check`, a `doc_check` citation that the
guard already runs, and two pytest self-check tests on citations. They are not
added, because one run each in five weeks does not pay for a check on every
push.

**They cost the push no time.** In a four-CPU session container, the guard's
three checks took 61 s side by side, bounded by `doc_check` alone at 59 s.
With the four added, side by side, the guard took 61 s: `workflow_paths_check`
4 s, `ignore_check` 3.5 s, `fixture_id_check` 10 s and the five line-split
tests 7 s. Run alone and cold, `ignore_check` took 23 s and the line-split file
43 s, both still inside `doc_check`'s time. The guard's comment still gives
`doc_check` 11 s, from `PL-PLSJ`'s measurement.

**They need the project's interpreter.** `fixture_id_check` parses `src/`,
which uses Python 3.14 syntax (`except OSError, subprocess.SubprocessError:` in
`app_metadata.py`). The guard runs its checks under the bare `python3`, which
is 3.13 here, so `fixture_id_check` dies there with a `SyntaxError`. Under
`.venv/bin/python`, the interpreter `make check`'s `uv run` uses, it passes.

**What made three sessions push past a failing local check.** The guard never
ran the check that failed. Seven of the 14 repeated pushes were
`r417-link-24` failing `ignore_check`, which the guard did not run. With
`ignore_check` in the guard, each of those pushes is refused in the session,
so why the session pushed does not need an answer.

**What to build.** `.claude/hooks/push-check-guard.sh` also runs
`tools/workflow_paths_check.py`, `tools/fixture_id_check.py`,
`tools/ignore_check.py` and `tests/unit/test_line_splits.py` under
`.venv/bin/python`, as `make check` runs them. A tree without that interpreter
skips the four, as a tree without a script skips that script. A refusal names
each one's re-run command, and the uncommitted-work note names them as readers
of the working tree.

**Done when.** A push whose tree fails any of the four is refused, naming the
check and its re-run command. A tree without `.venv/bin/python` runs the
other three checks and lets the push through where those pass.
`test_a_push_whose_project_interpreter_check_fails_is_refused` in
`tests/unit/test_push_check_guard.py` pins the refusal, and the guard's comment
records the measurement above.

**Generator check.** The fact is which of `make check`'s checks run before a
push leaves the session. `PL-0HPV` and `PL-ZQ3R`, both closed, hold the local
gate and the merge gate to one set of scripts. The push guard is a third set,
chosen on purpose as the cheap subset, so its gap is a selection the evidence
outgrew rather than a misread record. No open item names it, so this is a
one-off.
