---
id: PL-20CQ
title: "docket check runs every open item's verify: command, so a verify: that invokes docket check recurses without bound"
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_checks.py
added: 2026-09-01
verify: uv run pytest subprojects/docket/tests/test_checks.py -k recurs
---

**Problem.** `PL-3CBS` made `docket check` run every open item's `verify:`
command, to notice the ones that pass on a tree without their work. Nothing
stops one of those commands being `bin/docket check` itself. A single item
recording

    verify: ! bin/docket check 2>&1 | grep -q 'already passes'

makes `docket check` spawn a `docket check`, which spawns another, one level
per open item's turn, until the process table or the timeout gives out. It
would be run by `make check` and by CI, not only by whoever wrote it.

**Found how.** Not observed: it was the natural `verify:` command for
`PL-L9JS` (eight open items carry a command that passes without their work),
whose whole claim is about what `docket check`'s advisory reports. Writing it
would have been the first instance. `PL-L9JS` records `not-delegable:` instead,
with this as the reason, so the store is safe today by one person's judgment
rather than by a rule.

**Why it matters.** The blast radius is `make check` and CI rather than one
item, and the trigger is an ordinary-looking line that a session would write
for the most natural reason: an item *about* the queue's own checks is exactly
the kind whose proof is the queue's own checks. The failure is also confusing
in a way a stack trace does not fix - the outer run hangs, and nothing in its
output names the item that caused it.

Two adjacent commands are safe and should stay allowed: reading the store
(`grep` over `docs/items/`) and running any other `bin/docket` subcommand,
none of which executes a `verify:`. So the guard is narrower than "no
recursion into docket".

**Where.** `subprojects/docket/src/docket/checks.py` - the landed check that
runs the commands, and whatever validates a `verify:` line at `check` time so
the refusal lands on the item rather than on the run.

**Done when.** A `verify:` command that would re-enter `docket check` is an
error at `docket check` time, named on the item that records it, and the
message says which of the two safe shapes to use instead.
