---
id: PL-8F5B
title: Retire the check half of tools/dead_ends.py from make check and CI, and keep emit for the session-start digest
priority: P2
effort: S
status: done
classes: infra
feature: standing-weight
touches: Makefile, .github/workflows/quality.yml, tools/dead_ends.py, tests/unit/test_dead_ends.py, tests/unit/test_doc_check.py, docs/dead-ends.md, docs/apparatus.md, .claude/rules/dead-ends-apparatus.md, .claude/skills/docket/modes/triage.md, .claude/hooks/gate_status_guard.py, tests/unit/test_gate_status_guard.py, .claude/hooks/docket-digest.sh
added: 2026-11-21
closed: 2026-11-21
pr: 2185
payoff: make check and CI run one check fewer, and the dead-ends tool keeps only the half that prints the list at session start
verify: ! grep -qF 'dead_ends.py check' Makefile && ! grep -qF 'dead_ends.py check' .github/workflows/quality.yml && ! grep -qF 'def check' tools/dead_ends.py
---

**Problem.** Retire the check half of tools/dead_ends.py from make check and CI, and keep emit for the session-start digest

**Why it matters.** `PL-LY24` counted what each workflow-record check refused in CI from 2026-08-22 to 2026-11-21, and the owner agreed in `PL-KGPR` to retire this one (project owner, 2026-11-21, ratified, "Agree with recs"). `tools/dead_ends.py check` has never refused. The dead-ends list itself stays: `.claude/hooks/docket-digest.sh` still runs `tools/dead_ends.py emit` at session start.

**What to do.** Remove `tools/dead_ends.py check` from `make check` and `.github/workflows/quality.yml`, then remove the `check` subcommand and its tests. Keep `emit` and `docs/dead-ends.md`.

**Done when.** No command or workflow runs `tools/dead_ends.py check`, and the session-start digest still prints the entries.

**Triaged 2026-11-21: what the `check` half did.** It did three things, and all three go:

1. It refused an entry in `docs/dead-ends.md` that cites an id no item holds, an entry wrapped onto a second line, and a bullet that opens like an entry and is not in an entry's shape.
2. With `--base`, it refused an entry that left the list with no record of where it went (`PL-5J1S`).
3. It warned when the entries neared or passed 30 entries or 4,000 bytes. `tests/unit/test_dead_ends.py` keeps the shipped file below that warning, and that test stays, because it reads the `emit` half's output.

`emit` already prints a line in place of an entry that it cannot read whole (`PL-DQ9C`). The rules for editing the list stay in `docs/dead-ends.md`, and the grooming pass in `.claude/skills/docket/modes/triage.md` still re-tests the list.

**Generator check.** One-off. It is the removal that the owner decided in `PL-KGPR` from `PL-LY24`'s count, and no fact was misread to cause it.

**The evidence is eight chances, not 5,537.** `PL-LY24` counted no refusal from the check in 5,537 CI runs. The check reads one file, so it could refuse only on a branch that changed `docs/dead-ends.md`. Eight commits on `main` changed that file after the check entered CI on 2026-09-21 (`5bb363a24`, `#882`): `git log --first-parent origin/main 5bb363a24..origin/main -- docs/dead-ends.md` lists them. The check passed all eight. The owner's decision still applies, and this is the figure to quote for it.

**Done 2026-11-21.** `make check` and `.github/workflows/quality.yml` no longer run `tools/dead_ends.py check`, and the tool keeps only `emit`. The subcommand, its `--base` option and the code that only they used are deleted, with their tests. `.claude/hooks/gate_status_guard.py` no longer names the subcommand as a gate. The test that keeps the shipped file below 80% of both budgets stays and is now the budget's only enforcement. It compares the printed entries with the numbers directly, because the warning text it used to read is gone.

What is given up, as the tool's docstring and `docs/dead-ends.md` now say: a bullet that opens like an entry and is not in an entry's shape is not printed and nothing reports it, an entry can cite an id that no item holds, and an entry can leave the list with no record of where it went. `emit` still names an entry that a line carries on from the margin.

Documents checked, and changed where they said the check runs: `docs/dead-ends.md` (four passages of the preamble and the retired section's note), `docs/apparatus.md` (the tool list and the floor commands), `.claude/rules/dead-ends-apparatus.md`, `.claude/skills/docket/modes/triage.md` (the grooming pass), and the comment in `.claude/hooks/docket-digest.sh`. Checked and left: `CLAUDE.md`, `docs/maintainer.md`, `docs/worker.md` and `docs/resident-instructions.md` do not name the subcommand. The `Makefile` and `tools/doc_check.py` name the tool in dated accounts of `PL-PBP5`, which are still true.
