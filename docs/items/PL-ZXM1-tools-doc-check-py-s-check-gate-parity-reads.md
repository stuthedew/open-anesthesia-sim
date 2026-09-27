---
id: PL-ZXM1
title: tools/doc_check.py's check_gate_parity reads every run: line of a workflow triggered on pull_request as part of the merge gate, a step whose if: keeps it off pull requests included, so a script run only on a push to main passes as covered on every pull request: quality.yml's whole-store bin/docket check --verify step is one
status: untriaged
added: 2026-09-26
---

**Problem.** tools/doc_check.py's check_gate_parity reads every run: line of a workflow triggered on pull_request as part of the merge gate, a step whose if: keeps it off pull requests included, so a script run only on a push to main passes as covered on every pull request: quality.yml's whole-store bin/docket check --verify step is one

**Found 2026-09-26 while working `PL-RW3T`** (gate parity compares script
modes). `quality.yml` runs `bin/docket check --verify` under
`if: github.event_name != 'pull_request'`, so a pull request never runs it,
yet `check_gate_parity` counts it as merge-gate coverage because the workflow
is triggered on `pull_request` and the rule never reads a step's `if:`.
Matched by path alone this was invisible; matched by mode, `PL-RW3T` records
the step in `GATE_ONLY` as CI-only with that reason, which is honest about
this one step but leaves the rule blind to the next. The failure it allows is
the silent one: `make check` running `tools/x.py` while CI runs it only on a
push to `main` would pass parity and never gate a merge.

A fix reads a step's `if:` and leaves out a step whose condition excludes the
`pull_request` event; a condition it cannot read is declined through
`Report.declined` rather than guessed at, per
`.claude/rules/apparatus-standard.md`'s floor.
