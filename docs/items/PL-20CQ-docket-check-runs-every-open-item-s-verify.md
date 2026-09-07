---
id: PL-20CQ
title: "docket check runs every open item's verify: command, so a verify: that invokes docket check recurses without bound"
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.4.9
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md, tests/unit/test_ignore_check.py
added: 2026-09-01
closed: 2026-09-07
pr: 450
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

**Also repaired.** Adding one import line to `test_verify.py` turned
`tests/unit/test_ignore_check.py` red, and the test was wrong rather than the
change. It pinned a line number with `startswith("...test_verify.py:1")`,
meaning "the directive written inside a string literal, at 19x, is not
counted" - but a leading-digit prefix matches every line sharing it, so it
began matching the real directive at line 100 as soon as the file grew by a
line. It now locates the string-literal occurrence and asserts that one is
absent, which is what it meant to say.

**Decided (2026-09-07, project owner).** Option 2 of the three below: an
advisory, not an error, and scoped to the shape that can actually pass
vacuously rather than to `docket check` re-entry at large.

The options were (1) do nothing, since the vacuous shape has never been
written; (2) an advisory naming a `verify:` that pipes or captures `docket
check`'s output; (3) an error on that same shape. Two was taken because the
discriminator - whether a shell line reads a command's *output* or its *exit
status* - is a judgment rather than an exact rule, and `CLAUDE.md` reserves
hard failure for the exact ones.

`reads_check_output` implements it. A run of `docket check` followed by a pipe
before the pipeline ends, or one inside a command substitution, is reported;
the exit-status form is silent. The pipeline-end test is what keeps
`PL-39B7`'s recorded command correct - `bin/docket check && ! bin/docket
stranded | grep -qE ...` pipes `stranded`, not `check`, and the segment stops
at the `&&`.

Writing it also corrected the quoting model both predicates share. Blanking
every quoted span hid `test -z "$(bin/docket check)"`, because `$(...)` still
runs inside double quotes. `_outside_quotes` now blanks single-quoted spans
always and double-quoted ones only where they carry neither `$(` nor a
backtick, so reading the store stays allowed and a substitution stays visible.
