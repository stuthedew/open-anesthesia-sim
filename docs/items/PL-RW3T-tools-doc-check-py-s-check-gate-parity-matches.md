---
id: PL-RW3T
title: tools/doc_check.py's check_gate_parity matches a gate script by its path and not by the arguments it runs with, so a mode one gate runs and the other never does passes as covered: tools/pr_body_check.py --anchors ran only in make check from PL-73G8 until PL-3PH2, counted as covered in CI by pr-title.yml's --check, a different mode of the same script
priority: P2
effort: S
status: ready
classes: defect
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
payoff: a check wired into make check in one mode can no longer merge unenforced because CI happens to run the same script in another mode
verify: grep -q 'def test_gate_parity_refuses_a_mode_only_one_gate_runs' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py's check_gate_parity matches a gate script by its path and not by the arguments it runs with, so a mode one gate runs and the other never does passes as covered: tools/pr_body_check.py --anchors ran only in make check from PL-73G8 until PL-3PH2, counted as covered in CI by pr-title.yml's --check, a different mode of the same script

**Reach, measured 2026-09-26 on `claude/pr-body-storage-cnnpme`.** Comparing
the script invocations in `Makefile` against `quality.yml` and `pr-title.yml`
by script *and* arguments: once `PL-3PH2` added `--anchors` to `quality.yml`,
the only mode-level differences left are `pr_title_check.py --discover` and
`pr_record_check.py --discover`, which are the local stand-ins for what CI
reads from the event, so no live instance remains. The defect is the rule's
blindness to the next one: a mode added to one gate passes parity whenever
any other mode of the same script runs in the other.

**Reproduced 2026-09-26.** A fixture tree whose `check:` target runs
`python3 tools/x_check.py --anchors`, and whose one pull-request workflow runs
`python3 tools/x_check.py --check`, gets no error from `check_gate_parity`.
Read by script and mode, the gates here differ in four places, not two: the
two `--discover` runs above, and on CI's side `bin/docket check` at the 3.11
floor and `bin/docket check --verify` on a push to `main`, beside `make
check`'s `bin/docket check --verify --verify-base origin/main`.

**Why it matters.** The rule exists so that a check wired into one gate cannot
be missing from the other. Matched by path alone, it certifies a mode neither
gate compares, and it did so for `pr_body_check.py --anchors` from `PL-73G8`
until `PL-3PH2`: a check that passes while the guarantee it stands for is void.

**Done when.** `check_gate_parity` compares each gate's invocations by script
and mode, where a mode is the words ahead of the first option (a subcommand)
and the option names, with values dropped and order ignored. Every mode one
gate runs and the other does not is refused unless `GATE_ONLY` records it with
its reason, and the four standing differences are recorded. A test pins the
`--anchors` beside `--check` shape as refused.

**Exact match, not "covered by a superset of its options"** (the session that
built it, 2026-09-26). A superset rule would read CI's plain event-mode run as
covered by `--discover`, and any plain run as covered by a flagged one, but an
option can switch a script's mode rather than add to it (`--anchors` against
`--check`), and no tool can tell which without reading each script's parser.
Exact match reports the difference and asks for its reason, which is the
direction `.claude/rules/apparatus-standard.md`'s floor requires.

**Generator check.** The fact is `PL-0HPV`'s `misread:`, the checks the local
gate and the merge gate each run and where the two sets differ (head closed
2026-09-22, spent). This is an instance filed after that head closed: its fix
held the two lists together at the script level only. It is the first
post-close instance found.
