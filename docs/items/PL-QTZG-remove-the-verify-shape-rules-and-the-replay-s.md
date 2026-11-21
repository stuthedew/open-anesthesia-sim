---
id: PL-QTZG
title: Remove the verify: shape rules and the replay's reading of commands once items no longer carry them, about 1,640 lines of docket code with their tests
priority: P2
effort: M
status: blocked
classes: infra
feature: standing-weight
touches: subprojects/docket/src/docket, subprojects/docket/tests, subprojects/docket/README.md, docket.toml, Makefile, .github/workflows/quality.yml, .claude/skills/docket/modes/triage.md, .claude/skills/docket/modes/close-out.md, docs/apparatus.md, tools, tests/unit
blocked-by: PL-FN11, PL-N046, PL-NY7Q
added: 2026-11-21
payoff: about 1,640 lines that read and re-ran done-condition commands are gone, with the red runs the replay caused
---

**Problem.** Remove the verify: shape rules and the replay's reading of commands once items no longer carry them, about 1,640 lines of docket code with their tests

**Why it matters.** The project owner chose on 2026-11-21 that no item's done-condition is replayed after it closes (`PL-LFJZ`, the count of what a test-named done-condition would have prevented). That leaves the shape rules in `checks.py`, the command reading in `verify.py` and `grep.py`, and `bin/docket check --verify` with nothing to read. `PL-LY24` counted 9 episodes in which that replay caught a real mistake, all before 2026-09-23, and recommended retiring it with the commands; `PL-KGPR` (which of the 13 workflow-record checks to retire) holds that decision. `subprojects/docket/src/docket/shell.py` stays, because the Bash guard hooks and `tools/doc_check.py` read commands with it. This work comes after `PL-FN11`, `PL-N046` and `PL-NY7Q`.

**What to do.** Remove what only read or ran a `verify:` command, once `PL-FN11`, `PL-N046` and `PL-NY7Q` have merged:

1. `bin/docket check --verify` and `--verify-base`, the replay behind them, and their lines in the `Makefile` and `.github/workflows/quality.yml`.
2. The shape rules in `subprojects/docket/src/docket/checks.py`, their dates in `docket.toml` and `subprojects/docket/src/docket/config.py`, and the advisories that read a command.
3. The run of a command by `bin/docket set --verify` and by `bin/docket verify`, and `subprojects/docket/src/docket/grep.py`.
4. The sections of `subprojects/docket/README.md` and `.claude/skills/docket/modes/triage.md` that describe them.

The `verify:` field stays, because closed items record their command in it and `PL-N046`'s one clause is written there. `subprojects/docket/src/docket/shell.py` stays.

**Done when.** No code runs a `verify:` command through a shell, `bin/docket check` has no `--verify` flag, and `make check` passes.

**Generator check.** None: work the project owner chose in `PL-LFJZ` (the count of what a test-named done-condition would have prevented).
