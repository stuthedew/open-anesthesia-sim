---
id: PL-YYV9
title: triage.md's 'Run it and watch it fail' paragraph says docket check --verify raises an advisory that CI catches only after the push, but the replay has been an error since PL-71P4, make check runs it scoped to the branch, and since PL-FTDB bin/docket set --verify refuses a passing command as it is written
priority: P3
effort: S
status: ready
classes: docs
touches: .claude/skills/docket/modes/triage.md
added: 2026-09-26
payoff: a session writing a verify: at triage is told what actually refuses a command that already passes - set as it is written, make check before the push - and why watching it fail still matters once the tools do that
verify: grep -qF 'refuses one the replay would report as already passing' .claude/skills/docket/modes/triage.md && ! grep -qF 'raises an advisory for the ones that pass' .claude/skills/docket/modes/triage.md
---

**Problem.** triage.md's 'Run it and watch it fail' paragraph says docket check --verify raises an advisory that CI catches only after the push, but the replay has been an error since PL-71P4, make check runs it scoped to the branch, and since PL-FTDB bin/docket set --verify refuses a passing command as it is written

**Found 2026-09-26 closing `PL-FTDB`**, in its docs sweep; `PL-FTDB`'s
`touches` stop at `cli.py` and `test_cli.py`, so the paragraph was not its to
edit. `.claude/skills/docket/modes/triage.md` § "Run it and watch it fail, not
merely run it" says `docket check --verify` "raises an advisory for the ones
that pass" and that "CI is what passes that flag, so it is caught after the
item is written *and* after it is pushed". Three things have moved under it:
`checks.py` reports an open item whose command already passes as an error
(`PL-71P4`); the `Makefile`'s `check` target runs `bin/docket check --verify
--verify-base origin/main`, so a local `make check` replays every item the
branch changed; and `bin/docket set --verify` now runs the command it writes
and refuses one that already passes (`PL-FTDB`). The advice itself, to see the
command fail before recording it, still stands; only the account of when the
tools catch a skipped step is stale.

**Reproduced 2026-09-26 against 05559059.** `grep -n 'raises an advisory for
the ones that pass' .claude/skills/docket/modes/triage.md` finds the paragraph.
Against it: `checks.py`'s `_check_landed` appends the already-passes finding to
`report.errors`, under the comment "An error rather than an advisory since
`PL-71P4`"; the `Makefile`'s `check` target runs `bin/docket check --verify
--verify-base origin/main`, whose item scope `vcs._changed_items` reads from
the branch's commits and its uncommitted tree both; and `cli.py`'s `_replayed`
runs `already_passing` on the one item `set --verify` writes, pinned by
`test_set_refuses_a_verify_that_already_passes` (`PL-FTDB`). The same section
of triage.md already says it right further down: its paragraph "What the exit
status is read to mean once the command is recorded" has the replay report "an
open item whose command passes as an error".

**Why it matters.** A session writing a `verify:` at triage reads this
paragraph for what skipping the step costs, and is told the replay only
advises and only CI runs it, so the cost is a red run after the push. Neither
holds: the write itself is refused, or the next local `make check` is, and as
an error either way. The paragraph also contradicts its own section, and it
gives no reason for the advice that survives the tools now catching a command
that passes, so a reader who knows `set` replays the command is left with
nothing in the paragraph saying why running it first still matters. The advice
itself is unaffected, so nobody is steered to a wrong command by it, which is
why this is `P3`.

**Done when.** The paragraph says where a command that already passes is
refused - by `bin/docket set --verify` as it is written, and by `make check`
for a line written by hand - and why seeing it fail first still matters with
the tools doing that, and it no longer says the replay raises an advisory or
that CI is the first thing to catch it.

**Generator check.** A one-off, which `PL-FTDB`'s close-out docs sweep caught
as designed, the shape `PL-397Q` recorded. The fact misread is the link
between a document sentence and the tree fact it restates (`PL-4FBP`,
`PL-G424`, both closed 2026-09-19), and neither head's route claims this kind:
a claim about what three tools do is not a citation, and
`.claude/rules/citation-drift.md` leaves it to judgment and the capture rule on
purpose. Not `PL-0HPV`'s, though its change falsified the paragraph's middle
clause and its own commit added a sentence about the replay to the same section
without reaching this one: that head's fact is where the local and merge gates'
check sets differ, and they have not diverged again - the paragraph describes a
difference `PL-0HPV` removed.
