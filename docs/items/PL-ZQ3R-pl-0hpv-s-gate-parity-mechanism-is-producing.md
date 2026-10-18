---
id: PL-ZQ3R
title: PL-0HPV's gate-parity mechanism is producing again: tools/doc_check.py's check_gate_parity counts a command as run by a gate without reading the mode or condition it runs under, and four filings re-entered PL-0HPV after it closed spent
priority: P1
effort: M
status: ready
classes: defect
feature: gate-parity-conditions
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/items
deferred-from: v0.6.0 - captured after the freeze, workflow lane and not safety or science; as a live generator head it ranks above every band whatever the gate says
added: 2026-10-18
payoff: make check and CI are compared on what each actually runs on a pull request, so a check one gate skips under a condition or a mode is reported rather than counted as covered, and PL-0HPV's fact stops re-entering
verify: grep -q '^generator: spent' docs/items/PL-ZQ3R-*.md
root-cause-of: PL-RW3T, PL-ZXM1, PL-HSB3, PL-5M36
generator: live - check_gate_parity counts a command as run by a gate without reading the mode or the condition it runs under; four filings arrived from ordinary work after PL-0HPV closed on 2026-09-22, the last on 2026-10-10, and PL-ZXM1 and PL-HSB3 are still open
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
