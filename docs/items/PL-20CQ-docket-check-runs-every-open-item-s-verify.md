---
id: PL-20CQ
title: "docket check runs every open item's verify: command, so a verify: that invokes docket check recurses without bound"
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_verify.py
added: 2026-09-01
verify: uv run pytest subprojects/docket/tests/test_checks.py subprojects/docket/tests/test_verify.py && grep -q 'def test_a_verify_command_that_recurses_into_docket_verify_is_rejected' subprojects/docket/tests/test_checks.py
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

**Worked (2026-09-07).** The unbounded recursion is real, but not where this
item puts it. Two facts, both read off the tree rather than reasoned:

- `docket check` cannot recurse without bound, and could not when this item
  was written. `already_passing` runs the commands only under `--verify`,
  which `make check` does not pass and no recorded command passes; and a
  nested run is stopped by `LANDED_GUARD`, which landed with `PL-3CBS`
  itself. Two independent bounds. So the worked example under **Problem.**
  above does not fork-bomb - it fails a quieter way. The nested run declines
  the landed question, so the grep never matches, the leading `!` inverts
  that, and the command passes without ever observing the advisory it was
  written to test. Vacuous rather than explosive.
- `docket verify` does recurse without bound, and nothing guards it.
  `verify_item` shells out `item.verify` directly, so an item recording
  `verify: bin/docket verify PL-20CQ` runs itself once per level, each level
  taking a fresh 1800 s timeout rather than a share of one - so what ends it
  is the process table. This also falsifies the claim under **Why it
  matters.** that every other `bin/docket` subcommand is safe: exactly two
  execute a `verify:` field, and `verify` is the unguarded one.

So what shipped is the refusal that holds under either reading: a `verify:`
naming `docket verify` is an error at `docket check` time, named on the item,
and `verify_item` reports the re-entry as a failed check rather than recursing
where it is reached anyway. No open item records such a command, so nothing in
the store had to change. `reenters_verify` strips quoted spans before matching,
which is what keeps `grep -q 'docket verify' docs/items/` - reading the store,
one of the two shapes this item asked to leave allowed - from tripping it.

**Decision needed.** Whether anything should fire on a `verify:` that re-enters
`docket check`. The literal **Done when.** above asks for an error, and it must
not be built as written: ten open items record `bin/docket check && grep -q
...`, which is the paired shape `.claude/skills/docket/SKILL.md` recommends,
and erroring on it would fail `make check` on the store the rule exists to
protect. The narrower target is a command reading the nested run's *output*
rather than its exit status, which is the only shape that can pass vacuously.
Three answers, and the recommendation is the second:

1. Nothing. The vacuity is real but has never been written.
2. An advisory naming a `verify:` that pipes or captures `docket check`'s
   output, saying the nested run declines the landed question so the command
   cannot observe it. An advisory rather than an error because "reads the
   output" is a judgment about a shell line, and `CLAUDE.md` reserves hard
   failure for exact rules.
3. An error on that same shape, which has to be exact enough never to fire on
   the ten items above.
