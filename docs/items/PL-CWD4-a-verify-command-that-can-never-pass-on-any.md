---
id: PL-CWD4
title: A verify: command that can never pass on any tree is indistinguishable from one whose work is simply not done, so PL-4PC5 carried a dead command for five days after wave stopped printing the line it grepped
priority: P2
effort: M
status: done
classes: defect
feature: verify-command-meaning
touches: docs/items
added: 2026-09-19
closed: 2026-10-03
pr: 1297
verify: grep -qF 'Answered 2026-10-03: Q1 ratified' docs/items/PL-CWD4-a-verify-command-that-can-never-pass-on-any.md
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

**Re-pointed 2026-09-23 at `PL-1P5V`'s admitted shapes, which narrow this
rather than settle it.** `PL-4PC5`'s command read `wave`'s *output* through a
pipe, and no command captured from 2026-09-24 can take that shape. What can
still die is a `grep` whose target moves after the command is written: the file
renamed, or the line reworded. And the list makes one half of that decidable
for the first time. Every admitted command is `grep` clauses over named paths,
so `checks.verify_shape_refusal`'s parse can say which paths a positive clause
reads - and a path that neither exists in the tree nor falls under the item's
`touches` can never come to hold the pattern, because the work would have to
create it and work creating a file declares it. That is candidate 1 at the
altitude that holds. The pattern half of candidate 1 does not: a pattern
present nowhere is what every unstarted item's command looks like.

[superseded 2026-10-03: the count below found nothing for the file half to fire on; see the design round] **Recommended:** build the file half as an advisory on the admitted shapes -
advisory, since `touches` is a prediction a branch can outgrow - and record the
reworded-line half as undecidable (candidate 3), since a line the work will add
and a line another change reworded away read the same before the work.

## Design round 2026-10-03: recommendation

**Re-checked against the tree, 2026-10-03.** `checks.verify_shape_refusal`
admits `grep -q` and `! grep -q` over named paths and one whole-suite coverage
`pytest` shape, binding every command written from 2026-09-24
(`_verify_allowlist_applies`); `PL-4PC5`'s shape, reading `wave`'s output
through a pipe, is refused at write. No generator head is marked still
generating (`bin/docket generators`), so the pause on new mechanisms does not
decide this.

**The number, counted.** 189 open items carry a `verify:`; 125 are grep-only
shapes. The file half of candidate 1 - a positive clause naming a path that
neither exists in the tree nor falls under the item's `touches` - would fire
today on **0** of the 125 (a parse of the store on 2026-10-03; its three
apparent hits were two globs over the item's own file, which the shell expands
to a path that exists, and one pre-allowlist pipe shape). The store's whole
history holds one dead command, `PL-4PC5`, whose shape can no longer be
written. A check that fires on none of 125 commands earns no place by
`CLAUDE.md`'s own test, and its parser is upkeep paid for passes it never
saves.

**Q. Is a dead `verify:` distinguishable from an outstanding one by anything
the store can run, and if not, what is recorded instead?**
**Recommendation: do not build the advisory; record candidate 3, sharpened,
and close this item on the record.** The enforcement the brief said was
missing exists now: `PL-1P5V`'s allowlist checks a command on the branch that
writes it, so a command is live or refused at capture. The reworded-line half
is undecidable before the work, as the re-pointing above says. The file half is
decidable and has nothing to fire on. So the record is: a `verify:` that fails
is read as outstanding, and a dead one is found by the session that starts the
item, at the first replay that cannot pass - which is what `PL-4PC5` cost, five
days of a startable item, and what no second item has cost since.

**The cheapest build, if one is ever owed.** Not the parser: the replay
(`cli._replayed`, run scoped by `make check` since `PL-0HPV` and whole by
`bin/docket check --verify`) already runs every open command, and `grep` exits
2, not 1, when a file it names is missing - `-q` keeps that status where
nothing matched - so a dead path is already distinguishable from an unstarted
item by exit status alone. One branch on the replayed status, one test.

**What would change the answer.** A second open item whose `grep` names a path
that has since moved. One reopens this, with the exit-2 report as the build.

## Answers 2026-10-03

**Answered 2026-10-03: Q1 ratified** (project owner, 2026-10-03, ratified,
over building the file-half advisory on the admitted shapes, the filed
recommendation). Not built. The record: a `verify:` that fails is read as
outstanding; `PL-1P5V`'s allowlist is the enforcement at write; the
reworded-line half is undecidable before the work; and the file half had
nothing to fire on, 0 of 125 commands on 2026-10-03. A second open item whose
`grep` names a path that has since moved reopens this, with the replay's
`grep` exit-2 report as the build. Closed on this record in the design round's
own pull request, with no build thread.
