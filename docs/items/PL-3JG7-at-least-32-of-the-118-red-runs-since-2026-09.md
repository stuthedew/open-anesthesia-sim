---
id: PL-3JG7
title: At least 32 of the 118 red runs since 2026-09-21 that caught a real defect failed a check a local make check also runs: 18 whole-repository self-check tests in pytest, which the push guard does not run, and 14 repeated pushes on three branches past a failure make check reports
status: untriaged
feature: fewer-red-runs
touches: .claude/hooks
added: 2026-10-25
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
