---
id: PL-3DC7
title: bin/docket verify --self REJECTs any item with no verify: command and returns before running a single integrity check, so the close-out audit the docket skill says to re-run until ACCEPT is unreachable for the 118 dropped items and for every not-delegable: one
priority: P2
effort: M
status: dropped
classes: defect
feature: verify-close-out
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-17
closed: 2026-09-17
reason: already fixed on `main` by #655 (`PL-L4KX`), which landed while this triage pass was running. `subprojects/docket/src/docket/verify.py:746-758` is the narrow fix this item specified: `dropped` and a non-empty `not-delegable:` each produce an exemption string, the missing-command check is reported as an advisory rather than a failure, and `stopped_early` is not set - so the four integrity checks run and `ACCEPT` is reachable. The third half of the `Done when` holds too: `test_a_done_item_with_no_command_and_no_reason_still_fails_hard` pins that an item with neither still fails hard, beside `test_dropped_close_out_is_not_a_missing_command` and `test_a_not_delegable_item_close_out_is_not_a_missing_command`
---

**Problem.** bin/docket verify --self REJECTs any item with no verify: command and returns before running a single integrity check, so the close-out audit the docket skill says to re-run until ACCEPT is unreachable for the 118 dropped items and for every not-delegable: one

**Found closing `PL-879R`** (dropped 2026-09-17), at the close-out step that
runs the audit. `subprojects/docket/src/docket/verify.py:667`:

```python
if not item.verify:
    report.checks.append(Check("has a `verify:` command", False, "none recorded"))
    report.stopped_early = True
    return report
```

**It contradicts `docket check`, which decided this question the other way.**
`checks.py:336-346` holds a closed item to naming a command, and exempts two
cases explicitly: `not-delegable:`, and `dropped`. Its own comment says why -
"`dropped` is excluded: an item that will not be done carries a `reason`, not a
command for work nobody did." `docket check` passes a dropped item with 0
errors; `docket verify --self` REJECTs the same item in the same tree.

**The damage is the early return rather than the REJECT.** `stopped_early =
True` means none of the four integrity checks ran - no suppression check, no
removed-assertion check, no `make check`. The `docket` skill's own close-out
says "A `REJECT` that stopped early ran neither", and tells a session to re-run
until it says `ACCEPT`. For these items `ACCEPT` is unreachable, so the audit
cannot be satisfied and must be ignored: the session either skips the step or
reads a REJECT that measured nothing. That is `PL-69JZ`'s failure - "a defect
absorbed into policy" - arriving in the command whose docstring cites it.

**The population is not marginal.** 118 items in the store are `dropped`, five
of them closed on 2026-09-16 alone, plus every item recording `not-delegable:`
- the answer the skill calls honest where no command can prove the work.

**The narrow fix, and the reason it is narrow.** Where `item.verify` is empty
*and* the store's own rule exempts the item - `status: dropped`, or a
`not-delegable:` reason recorded - report the missing command as a `NOTE` and
carry on to the four integrity checks, rather than returning. Nothing is
weakened: the "item's own command passes" check has no command to run and
should say so, while "no suppression added", "no assertion removed" and "`make
check` passes" are exactly as applicable to a drop as to a close, and are the
checks that currently do not run. An item that is neither dropped nor
`not-delegable:` and carries no command still fails, which is the case the guard
was written for.

**Done when** `bin/docket verify --self` on a dropped item runs the four
integrity checks and can reach `ACCEPT`, an item with neither a command nor an
exemption still fails, and both are covered by tests.

**Why it matters.** The close-out audit is the last gate before an item is
declared finished, and `.claude/skills/docket/SKILL.md` step 5 tells a session to
re-run it until it says `ACCEPT`. For the 118 dropped items and every
`not-delegable:` one, `ACCEPT` is unreachable - so the instruction cannot be
followed and the session must either skip the step or read a `REJECT` that
measured nothing. That is `PL-69JZ`'s "defect absorbed into policy", arriving in
the command whose docstring cites it, and it trains a reader to skim the block
where a real protected-path failure prints.

The damage is the early return rather than the verdict: `stopped_early = True`
means no suppression check, no removed-assertion check and no `make check` ran on
a diff that is about to land.

**Done when** `bin/docket verify --self` on a dropped item, and on one recording
a `not-delegable:` reason, runs the four integrity checks and can reach `ACCEPT`;
an item that is neither and names no command still fails; and both are covered by
tests.

**Grouped under `feature: verify-close-out`** at triage, with `PL-7TYC` and
`PL-TKFD` from `#655` - the same audit, the same three states it has no clean
route through.

**Dropped at triage, 2026-09-17, as work already done** (project owner, who
named the landed branch and its line numbers).

**One thing worth carrying out of it, because it is the store's own hazard
showing up in this pass.** This item was triaged to `ready` an hour earlier with
the command

```
uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_dropped_item_naming_no_command_still_runs_the_integrity_checks' subprojects/docket/tests/test_verify.py
```

which was run and seen to exit 1, exactly as the rule asks. It failed for the
wrong reason: the behaviour was already on `main` under three differently-named
tests, and the `grep` half was pinning a *name* nobody had agreed to rather than
a behaviour. A paired command proves the tree is healthy and that some test is
called what the item guessed - it cannot prove the behaviour is absent. So
"watch it fail for the right reason" needs one step this session did not take:
read the code the item says is broken, not only the test names. `PL-6YWK` and
`PL-XMNC` are the items already circling this from other directions.
