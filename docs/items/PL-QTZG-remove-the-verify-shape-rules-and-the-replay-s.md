---
id: PL-QTZG
title: Remove the verify: shape rules and the replay's reading of commands once items no longer carry them, about 1,640 lines of docket code with their tests
priority: P2
effort: M
status: done
classes: infra
feature: standing-weight
touches: subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md, docket.toml, Makefile, .github/workflows/quality.yml, .claude/skills/docket/modes/triage.md, .claude/skills/docket/modes/close-out.md, .claude/skills/docket/modes/capture.md, .claude/skills/docket/modes/design.md, .claude/skills/docket/modes/release.md, .claude/hooks, docs/apparatus.md, docs/worker.md, tools, tests/unit
added: 2026-11-21
closed: 2026-11-21
pr: 2188
payoff: about 1,640 lines that read and re-ran done-condition commands are gone, with the red runs the replay caused
tests: subprojects/docket/tests/test_verify.py::test_an_item_s_search_is_read_whether_or_not_the_item_has_closed, subprojects/docket/tests/test_verify.py::test_an_open_item_s_command_is_reported_as_not_run, subprojects/docket/tests/test_cli.py::test_set_refuses_a_search_that_is_true_before_the_work, subprojects/docket/tests/test_cli.py::test_check_runs_no_item_s_command
---

**Problem.** Remove the verify: shape rules and the replay's reading of commands once items no longer carry them, about 1,640 lines of docket code with their tests

**Why it matters.** The project owner chose on 2026-11-20 that no item's done-condition is replayed after it closes (`PL-LFJZ`, the count of what a test-named done-condition would have prevented). That leaves the shape rules in `checks.py`, the command reading in `verify.py` and `grep.py`, and `bin/docket check --verify` with nothing to read. `PL-LY24` counted 9 episodes in which that replay caught a real mistake, all before 2026-09-23, and recommended retiring it with the commands; `PL-KGPR` (which of the 13 workflow-record checks to retire) holds that decision. `subprojects/docket/src/docket/shell.py` stays, because the Bash guard hooks and `tools/doc_check.py` read commands with it. This work comes after `PL-FN11`, `PL-N046` and `PL-NY7Q`.

<!-- absent: grep.py -->

**What to do.** Remove what only read or ran a `verify:` command, once `PL-FN11`, `PL-N046` and `PL-NY7Q` have merged:

1. `bin/docket check --verify` and `--verify-base`, the replay behind them, and their lines in the `Makefile` and `.github/workflows/quality.yml`.
2. The shape rules in `subprojects/docket/src/docket/checks.py`, their dates in `docket.toml` and `subprojects/docket/src/docket/config.py`, and the advisories that read a command.
3. The run of a command by `bin/docket set --verify` and by `bin/docket verify`, and `subprojects/docket/src/docket/grep.py`.
4. The sections of `subprojects/docket/README.md` and `.claude/skills/docket/modes/triage.md` that describe them.

<!-- absent: subprojects/docket/src/docket/grep.py -->

The `verify:` field stays, because closed items record their command in it and `PL-N046`'s one clause is written there. `subprojects/docket/src/docket/shell.py` stays.

**Done when.** No code runs a `verify:` command through a shell, `bin/docket check` has no `--verify` flag, and `make check` passes.

**Generator check.** None: work the project owner chose in `PL-LFJZ` (the count of what a test-named done-condition would have prevented).

**Built 2026-11-21.** The branch removes about 7,000 lines: 3,067 from `subprojects/docket/src/docket`, 3,193 from its tests, and the rest from the `Makefile`, `.github/workflows/quality.yml`, the tools and the documents. What went:

1. `bin/docket check --verify` and `--verify-base`, the replay behind them, the scoped and whole-store steps in `.github/workflows/quality.yml`, and the replay line in the `Makefile`. Both gates now run one store check, `bin/docket check`.
2. Every rule in `checks.py` that read a command's text: the shape rules, the rule on two open items sharing one command, and the advisories that read a command. `docket.toml` and `config.py` keep `verify_required_at_close_from` and `collected_test_paths`.
3. The shell run of a command by `bin/docket set --verify` and by `bin/docket verify`, and `grep.py` with its tests.
4. What read the replay's result outside docket: the replay branch of `tools/main_ci_status.py`, the `DOCKET_WORKER_ITEM` variable that `tools/headless_worker.py` set for the replay, and the `--verify` words of the store check in `.claude/hooks/push_check_guard.py`.

<!-- absent: grep.py -->

**Decisions taken while building.** Each kept a guard that the removed code gave, without a shell.

1. `bin/docket verify` reads an open item's text search as well as a closed item's record, because a delegated worker leaves its item open and the reviewer's audit is the only reader of that search before the close. An open item that still carries a command written before 2026-11-21 gets an advisory line that says the command was not read.
2. `bin/docket set --verify` refuses, on an open item, a search that is already true on the tree and a search that reads the item's own file. The removed run of the command refused both, and either search would show nothing when the item closes. `done.true_before_the_work` holds the rule.
3. The rule on two open items sharing one command went with the other rules, because nothing runs a command and a shared search is read once for each item when it closes.
4. `done.keeps_its_command` is the one place that says which items may keep a `verify:` that is not a search: a release item and an item that records `not-delegable:`.

**Documents checked.** `subprojects/docket/README.md`, `docs/apparatus.md`, `docs/worker.md`, `docs/maintainer.md`, `CLAUDE.md`, `docket.toml`, the `Makefile`'s comments, `.claude/hooks/push_check_guard.py`, `.claude/hooks/docket-digest.sh`, and under `.claude/skills/docket/` the files `SKILL.md`, `modes/triage.md`, `modes/close-out.md`, `modes/capture.md`, `modes/design.md`, `modes/release.md`, `modes/start.md` and `modes/picking.md`. `ROADMAP.md`, `docs/releases/`, `docs/pr-bodies/`, `docs/WORKING_NOTES.md` and closed items still describe the replay, as records of their date.
