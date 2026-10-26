---
id: PL-3JG7
title: At least 32 of the 118 red runs since 2026-09-21 that caught a real defect failed a check a local make check also runs: 18 whole-repository self-check tests in pytest, which the push guard does not run, and 14 repeated pushes on three branches past a failure make check reports
priority: P2
effort: M
status: ready
classes: infra
feature: fewer-red-runs
touches: .claude/hooks/push-check-guard.sh, tests/unit/test_push_check_guard.py
added: 2026-10-25
payoff: a push that a whole-repository self-check test would refuse is refused on the session's machine, not in a CI run
verify: grep -qF 'test_workflow_paths_check' .claude/hooks/push-check-guard.sh
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

**Reproduced 2026-10-26.** `.claude/hooks/push-check-guard.sh` runs three
checks before a push: `doc_check`, `branch_id_check` and `bin/docket check
--verify`. None of them is a `pytest` run, so a whole-repository self-check
test such as `test_workflow_paths_check.py` or `test_fixture_id_check.py`
first runs in CI.

**Done when.** The push guard also runs the whole-repository self-check tests
named above, `test_workflow_paths_check.py` and `test_fixture_id_check.py` at
least, unless a timing shows they make the guard too slow. The brief then
records that timing either way. It also records why three branches pushed
again past a failing `make check`. Where that cause needs a change of its own,
it is filed as a new item.

**Generator check.** The closest heads are `PL-0HPV` and `PL-ZQ3R`, whose fact
is which checks the local gate and the merge gate each run. Those two gates
still agree here, because all 32 runs failed `make check` too. The push guard
is a chosen subset of `make check`, so this item asks which checks that subset
should hold. Nobody misread a gate's set, so it is a one-off.
