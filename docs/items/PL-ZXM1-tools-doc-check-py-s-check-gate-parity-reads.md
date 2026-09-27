---
id: PL-ZXM1
title: tools/doc_check.py's check_gate_parity reads every run: line of a workflow triggered on pull_request as part of the merge gate, a step whose if: keeps it off pull requests included, so a script run only on a push to main passes as covered on every pull request: quality.yml's whole-store bin/docket check --verify step is one
priority: P3
effort: S
status: ready
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: a script CI runs only on a push to main can no longer pass gate parity as merge-gate coverage, so a check cannot merge unenforced behind a step condition
verify: grep -q 'def test_gate_parity_leaves_out_a_step_whose_if_excludes_pull_requests' tests/unit/test_doc_check.py
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

**Reproduced 2026-09-27** in a scratch tree: a `Makefile` whose `check` runs
`tools/x_check.py` and `tools/y_check.py`, and a `quality.yml` triggered on
`pull_request` and `push` whose only step runs `tools/x_check.py` under `if:
github.event_name != 'pull_request'`. `check_gate_parity` reported `y_check.py`
as run by no pull-request workflow and passed `x_check.py` as covered, though
no pull request runs it. `workflow_commands` yields every `run:` line of a
workflow `_gates_pull_requests` admits, and neither reads a step's `if:`.

**Why it matters.** Gate parity is what stops a check merging unenforced, and
it passes a script the merge gate never runs whenever the step running it is
conditioned off pull requests. The one such step today is recorded in
`GATE_ONLY` by hand, naming this item, so nothing is unenforced now; the next
conditioned step would pass silently, which is the check reporting a guarantee
that does not hold.

**Done when.** `check_gate_parity` leaves out of the merge gate a step whose
`if:` excludes the `pull_request` event, declines through `Report.declined` a
condition it cannot read rather than guessing at it, and a test pins both;
`GATE_ONLY`'s `bin/docket check --verify` entry, recorded there because the
rule could not read an `if:`, is removed or restated to match.

**Generator check.** An instance of `PL-0HPV`'s fact - the checks the local
gate and the merge gate each run, and where the two sets differ - filed after
that head closed (2026-09-22, `spent`). It is the second: `PL-RW3T`, the first,
taught the rule a script's mode and found this while doing so. One short of the
three that would record `PL-0HPV`'s fix as not holding.
