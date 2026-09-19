---
id: PL-CWD4
title: A verify: command that can never pass on any tree is indistinguishable from one whose work is simply not done, so PL-4PC5 carried a dead command for five days after wave stopped printing the line it grepped
priority: P2
effort: M
status: needs-decision
classes: defect
feature: verify-command-meaning
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-19
---

**Problem.** A verify: command that can never pass on any tree is indistinguishable from one whose work is simply not done, so PL-4PC5 carried a dead command for five days after wave stopped printing the line it grepped

**The mechanism.** A `verify:` command is written to fail before the work and pass
after, and `bin/docket check --verify` replays the open store's commands to report
the ones that already pass. A command whose *target* has since disappeared - the
line it greps for reworded, the file it names moved, the output it reads no longer
printed - fails forever, and fails identically to a command whose item simply has
not been started. Nothing in the store separates the two, so the dead one is
ranked, offered by `bin/docket next`, and counted into a debt gate exactly as live
work is.

**The instance.** `PL-4PC5` carried such a command for five days after `wave`
stopped printing the line it grepped. The item stayed startable throughout and the
command could not have passed on any tree in that window.

**Why it matters.** It is the exact mirror of the trap the replay already catches,
and the asymmetry is why nobody sees it. A command that has started *passing* is
reported, because a `ready` item whose proof already holds is visibly wrong. A
command that can never pass is not, because "this command fails" is the expected
state of every unstarted item in the store - so the store's silence carries two
meanings and a reader cannot tell which one is in front of them. The cost lands on
the item's eventual session, which starts work against a proof that will not go
green however correct the work is, and which has no reason to suspect the command
rather than itself.

**Not `PL-0QRP`**, which is a command that starts *passing* without the work, and
not `PL-BX1C`, which is a command correctly failing on an item that was dropped.

**Done when.** A `verify:` command whose failure cannot be cleared by doing its
item's work is distinguishable from one that is merely outstanding - by a check
that reports it, by a recorded convention that makes the difference decidable, or
by this item recording why the two cannot be told apart without running the work.
`PL-4PC5`'s case is the test either way.

**Decision needed.** Whether a dead `verify:` command is distinguishable from an
outstanding one *by anything the store can run*, and if not, what the store
records instead. Three candidates, none costed:

1. **A staleness advisory on the command's target** - report a `grep`-shaped
   command whose pattern matches nothing anywhere in the tree, on the argument
   that a pattern present nowhere cannot be the thing the work adds. Cheap and
   decidable; it catches the reworded-line case and misses a command whose
   pattern still appears somewhere irrelevant.
2. **Re-run the command at the moment the item is started**, and treat a failure
   whose shape has not changed since capture as suspect. Closer to the truth and
   far more expensive; `PL-FZ58` measures what replaying the store's commands
   already costs.
3. **Record that it is undecidable** and put the weight on the author instead -
   the command is written *having been run*, and a command that was run once
   cannot have been dead at capture. That is already the rule; this ending says
   the gap is enforcement of it rather than detection.

The third is the cheapest and is the one to argue against first: `PL-4PC5`'s
command was live when written and died afterwards, which no authoring rule
reaches.
