---
id: PL-HS2T
title: Retire tools/branch_id_check.py from make check, CI and the push hook
priority: P2
effort: M
status: done
classes: infra
feature: standing-weight
touches: .claude/hooks/docket_branch_guard.py, .claude/hooks/push_check_guard.py, .claude/skills/docket/modes/capture.md, .claude/skills/docket/modes/start.md, .github/workflows/quality.yml, Makefile, docket.toml, docs/apparatus.md, docs/resident-instructions.md, subprojects/docket/README.md, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_claims.py, subprojects/docket/tests/test_vcs.py, tests/unit/test_branch_id_check.py, tests/unit/test_docket_branch_guard.py, tests/unit/test_floor_interpreter_guard.py, tests/unit/test_main_ci_status.py, tests/unit/test_push_check_guard.py, tests/unit/test_tools_portability.py, tests/unit/test_workflow_paths_check.py, tools/branch_id_check.py, tools/fixture_id_check.py, docs/items/PL-PNB2-replace-each-paragraph-of-the-instructions.md, docs/items/PL-TPXK-review-the-four-streamlining-decisions-of-2026.md
added: 2026-11-21
closed: 2026-11-21
pr: 2185
payoff: a session's push and its pull request are no longer refused for a missing claim on work that other sessions could already see, and 1,400 lines of tool and test leave the tree
verify: ! grep -qF 'branch_id_check' Makefile && ! grep -qF 'branch_id_check' .github/workflows/quality.yml && ! grep -qF '"tools/branch_id_check.py"' .claude/hooks/push_check_guard.py && ! grep -qF 'hint-changed' .claude/hooks/docket_branch_guard.py
---

**Problem.** Retire tools/branch_id_check.py from make check, CI and the push hook

**Why it matters.** `PL-LY24` counted what each workflow-record check refused in CI from 2026-08-22 to 2026-11-21, and the owner agreed in `PL-KGPR` to retire this one (project owner, 2026-11-21, ratified, "Agree with recs"). Its 12 refusals caught no mistake: 10 asked for a claim on a branch whose commit subjects already named its item, and 2 were the owner's own edit on GitHub's web page. It has cost 21 items. `bin/docket claim` still writes claims.

**What to do.** Remove the check from `make check`, `.github/workflows/quality.yml` and the push guard hook, then delete the tool and its test. Leave the claim record alone.

**Done when.** No command, workflow or hook runs `tools/branch_id_check.py`, and the file and its test are gone.

**Triaged 2026-11-21: what goes with the tool.** The tool made three refusals, and all three go:

1. A `claude/*` branch that no item id names, in its name or at the front of a commit subject (`PL-CP74`).
2. A `claude/*` branch that changed a path outside the queue and claims nothing (`PL-J9S0`).
3. A branch whose claim on an item orders behind another branch's live claim on it (`PL-J9S0`).

`PL-LY24`'s 12 refusals were 10 of the second kind and 2 of the first, which were the owner's own edit on GitHub's web page. The third kind never refused in CI. `bin/docket claim` still refuses a second claim when it is written: it exits 3 and writes nothing where another branch holds the item first. `bin/docket show` still prints the order of the claims on an item. `bin/docket flight` still lists a branch that no id names, and a branch with work and no claim as `unclaimed:`. So after this item a second claim written past `claim`'s refusal is reported and no longer refused.

The tool has two more callers than this brief first named. `.claude/hooks/docket_branch_guard.py` asked it, at a session's first edit, whether the branch claimed an item (`--hint` and `--hint-changed`). That question goes with the tool, and the hook keeps its other question, whether `main` has moved. Moving the question into the hook would rebuild the check that the owner retired. `quality.yml` ran the tool twice, once under the bare interpreter and once under `uv run`.

**Generator check.** One-off. It is the removal that the owner decided in `PL-KGPR` from `PL-LY24`'s count, and no fact was misread to cause it.

**Done 2026-11-21.** `make check`, both steps in `.github/workflows/quality.yml` and `.claude/hooks/push_check_guard.py` no longer run the tool, `.claude/hooks/docket_branch_guard.py` no longer asks it, and `tools/branch_id_check.py` and `tests/unit/test_branch_id_check.py` are deleted. The push guard's tests that used the tool as their second check now use `doc_check` and the store check.

Documents checked, and changed where they said the check runs: `docs/apparatus.md` (the tool list, the paragraphs on the guard, the two-way run and the floor commands), `docs/resident-instructions.md` (three rows of the table of what catches each resident rule, and the housekeeping paragraph), `.claude/skills/docket/modes/start.md`, `.claude/skills/docket/modes/capture.md`, `subprojects/docket/README.md`, and the comments in `docket`'s `render.py`, `vcs.py`, `claims.py`, `checks.py` and `cli.py` that said the check keeps `flight`'s lines empty. Checked and left: `CLAUDE.md`, `docs/maintainer.md` and `docs/worker.md` do not name the tool. `tools/workflow_paths_check.py` names it in a dated account of 2026-09-06, which is still true.

