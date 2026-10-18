---
id: PL-ZQ3R
title: PL-0HPV's gate-parity mechanism is producing again: tools/doc_check.py's check_gate_parity counts a command as run by a gate without reading the mode or condition it runs under, and four filings re-entered PL-0HPV after it closed spent
priority: P1
effort: M
status: done
classes: defect
feature: gate-parity-conditions
touches: tools/doc_check.py, tools/required_checks_check.py, tests/unit/test_doc_check.py, tests/unit/test_makefile_reference.py, docs/items
deferred-from: v0.6.0 - captured after the freeze, workflow lane and not safety or science; as a live generator head it ranks above every band whatever the gate says
added: 2026-10-18
closed: 2026-10-18
payoff: make check and CI are compared on what each actually runs on a pull request, so a check one gate skips under a condition or a mode is reported rather than counted as covered, and PL-0HPV's fact stops re-entering
verify: grep -q '^generator: spent' docs/items/PL-ZQ3R-*.md
root-cause-of: PL-RW3T, PL-ZXM1, PL-HSB3, PL-5M36
generator: spent - check_gate_parity now reads what each command runs under on both sides: a script's mode (PL-RW3T), the if: of a workflow step and of its job, and a Makefile conditional, which it declines; a condition it cannot evaluate is declined by name, so no command reaches either gate's set without its condition read, and a new condition form can only add a decline, never a false match
misread: The checks the local gate and the merge gate each run, and where the two sets differ
reenters: PL-0HPV
---

**Problem.** PL-0HPV's gate-parity mechanism is producing again: tools/doc_check.py's check_gate_parity counts a command as run by a gate without reading the mode or condition it runs under, and four filings re-entered PL-0HPV after it closed spent

**Why it matters.** `PL-0HPV` closed spent on 2026-09-22. Its verdict said
`check_gate_parity` keeps `make check` and CI's `quality.yml` from drifting
apart at the script level. Four filings have re-entered its fact since then.
`PL-RW3T` (closed) found that gate parity matched a script by its path and
ignored its mode, so `pr_body_check.py --anchors` counted as covered.
`PL-ZXM1` (open) found that it counts a workflow step whose `if:` keeps it off
pull requests. `PL-HSB3` (open) found that it counts a recipe line inside a
Makefile conditional as running in every configuration. `PL-5M36` (closed)
found that it reported a difference after declining a line it could not read.
Each time, a check that one gate skips reads as covered, so a pull request can
pass `make check` and fail CI, or the reverse, with gate parity reporting
nothing. `PL-SH4H` answered `bin/docket inflow`'s line for `PL-0HPV` with this
item.

**Not a narrower head.** `PL-848V` reads only a workflow's `on:` triggers, not
a step's `if:`. `PL-R417` reads only lines that continue a statement.
`PL-GSJ6` and `PL-MB3F` are recorded as one-offs.

**Done when.** `PL-ZXM1` and `PL-HSB3` are fixed by one design: gate parity
reads the condition and the mode each command runs under, or declines that
command by name, so it never counts a command as run on a pull request that
only runs in some configurations. Then this item records the bound that makes
its mechanism spent, and closes with `generator: spent - <why>`.

**Generator check.** This is the successor head for `PL-0HPV`, recorded by
`PL-SH4H` on 2026-10-18 (`reenters: PL-0HPV`).

**Next steps, 2026-10-18 13:30Z.** Stuart agreed at 13:08Z that the
"Workflow items, third place" thread fixes this item next. That thread
stopped for length before claiming it, so a fresh thread takes it up.

1. Run `bin/docket flight` and `bin/docket concurrent PL-ZQ3R`. `PL-JTCQ`
   also declares `tools/doc_check.py` and `tests/unit/test_doc_check.py`,
   for `_baseline` and `_deleted_paths`, which are different functions. The
   one-answer thread ("One-answer items, batch five") was asked at 13:27Z to
   agree that both proceed and the second to merge brings `main` in. Read
   its answer before claiming.
2. Claim `PL-ZQ3R`, `PL-ZXM1` and `PL-HSB3` together.
3. `PL-ZXM1`: `workflow_commands` yields every `run:` line of a workflow that
   `_gates_pull_requests` admits. Read each step's `if:`, leave out a step
   whose condition excludes the `pull_request` event, and decline through
   `Report.declined` a condition the reader cannot parse. Then remove or
   restate the `GATE_ONLY` entry for `bin/docket check --verify`, which was
   recorded by hand because the rule could not read an `if:`.
4. `PL-HSB3`: `_make_lines` reads every branch of a Makefile conditional.
   Make `make_targets` and `check_gate_parity` count a recipe line inside a
   conditional as running only in its branch, or decline such a target by
   name. Keep the coverage-gate and ruff-cache readers, which rightly hold
   every command make might run.
5. Pin each with a test that fails on the code before the fix. Then record
   the bound in this item's `generator:` as `spent - <why>`, which its
   `verify:` tests, and close all three.

**Fixed 2026-10-18, with `PL-ZXM1` and `PL-HSB3`.** One rule now applies to
both gates: a command counts as run by a gate only where every pull request
runs it, and a condition the reader cannot settle is declined by name. On the
merge gate, `pull_request_runs` reads each step's and job's `if:`. On the
local gate, `_target_recipes` declines a recipe line inside a Makefile
conditional. With `PL-RW3T`'s mode reading, the three ways a command could be
counted without its condition read are closed. `PL-5M36` already made any
decline stop the comparison. A new condition form can now only add a decline,
which the check prints, and never a false match, so the mechanism is spent.
