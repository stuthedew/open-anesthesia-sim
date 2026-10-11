---
id: PL-2C53
title: Re-point PL-R808's six open generator members at tools/left_behind_check.py, closing each whose question the exact left-behind check now answers
priority: P2
effort: M
status: done
classes: housekeeping
feature: parallel-sessions
milestone: v0.5.23
touches: docs/items
added: 2026-09-23
closed: 2026-10-11
pr: 1396
payoff: no session spends an item building another vcs.py heuristic for a member the exact check already answers: each of the six either closes on it or says what it still owns
verify: grep -qF 'left_behind_check.py' docs/items/PL-X5PK-*.md && grep -qF 'left_behind_check.py' docs/items/PL-CZR6-*.md && grep -qF 'left_behind_check.py' docs/items/PL-NPWP-*.md && grep -qF 'left_behind_check.py' docs/items/PL-BYMX-*.md && grep -qF 'left_behind_check.py' docs/items/PL-B78T-*.md
---

**Problem.** Re-point PL-R808's six open generator members at tools/left_behind_check.py, closing each whose question the exact left-behind check now answers

**Reproduced 2026-09-23.** `bin/docket generators` lists `PL-R808` with seven
members, six of them open: `PL-X5PK`, `PL-CZR6`, `PL-NPWP`, `PL-BYMX`,
`PL-B78T` and `PL-1X2C`, all at `ready`. None of the six files mentions
`left_behind_check` or `PL-R808` (`grep -c` gives 0 in each), so none has been
re-pointed. `docket next` can offer all six now, five of them at `P2`. A
session that starts one would build another content, date or subject heuristic
in `vcs.py`. `PL-R808`'s `spent` verdict says a member no longer needs one. Two
of them cite the instance the check now reports. `PL-B78T`'s title names the
206 lines of docket source on `claude/recurrence-signal-feature-3hnynt` (that
is `PL-SRBR`), and `PL-CZR6`'s names commits pushed to a branch after its pull
request squash-merged.

**What the check reaches, for the pass to weigh member by member.** It runs in
the session-start digest, not inside any `docket` command, because `PL-SK88`
keeps the harness out of `docket`. It needs a token and the network. It
answers only for a branch whose newest pull request merged. Every decline stays
with `vcs.orphaned` (`PL-BHVM`). So a
member whose defect is in what `docket stranded`, `flight` or `show` prints is
not answered just because the digest now prints a line. That member keeps its
place, and its brief says what the exact check now covers and what is still
left to it.

**Re-confirmed 2026-10-11, with five members rather than six.** `PL-1X2C`
closed on 2026-09-26 in `#1046` on its own fix: `bin/docket show` now names
every other branch editing an item and leaves out the reader's own. That is a
question about carriers, which reads no landing and nothing the exact check
reports, so it leaves this pass and the `verify:` names the other five. Two
corrections to the paragraph above, both read from the tree. It said a branch
with no pull request stays with `vcs.orphaned`; it is read by neither check.
`left_behind_check.py` clears it ("no pull request was opened from it"), and
`vcs.orphaned` reports a branch only where part of its work has landed, so only
`stranded`'s item reading sees one. And the check has a second reader since
filing: `tools/branch_sweep.py` (`PL-X8SV`) keeps a branch the check reports or
cannot read, so the daily sweep never archives a commit it names.

**Generator check.** Bookkeeping. The head's own members were left to re-point,
and this item was filed in the commit that closed `PL-R808` (`#932`). That is
the shape `PL-04KR` records for every attributed child to date. The store holds
no other re-point item, so there is no cluster to name.

**Done 2026-10-11.** Each of the five was weighed against the check, and against
the tree where the tree had moved, and two shapes were reproduced on scratch
repositories with real git:

- `PL-CZR6` keeps its place, re-scoped. Its question is the check's own: the
  check names such a commit at every session start and keeps its branch from
  the sweep, so no further content reading in `vcs.py` is owed. What is left is
  the line `bin/docket stranded` prints. Reproduced: after a squash against a
  moved base and a push afterwards, `stranded` says "No branch carries work its
  own pull request left behind" while the check names the commit. It is now `S`
  and touches `render.py` and `test_cli.py`.
- `PL-NPWP` keeps its place, re-scoped. The check opens no item copy. The
  untouched copy its brief names was fixed by `PL-WVSX` in `#1160`, which the
  reproduction confirms. What is left, also reproduced, is a copy a squash
  merged with another edit and the base then reworded, which
  `vcs.change_landed` already answers.
- `PL-B78T` is dropped as `PL-BYMX`'s duplicate. Its two instances were settled
  elsewhere, one of them by the check's first live finding (`PL-SRBR`), and its
  Done-when is `PL-BYMX`'s question.
- `PL-BYMX` keeps its whole design question, since the check clears a branch
  with no pull request before comparing anything. It takes `PL-B78T`'s
  closed-unmerged shape, its place in `stranded-report-fidelity`, and the
  sweep's archive, which changes what its "nothing at all" answer costs.
- `PL-X5PK` is about `flight`, which the check does not read. Its brief now
  records that the reader it quotes was replaced and that the digest deepens a
  shallow checkout.

So one member closes, and one keeps only what `stranded` prints. The other three
share `PL-R808`'s misread but were never answerable by its check, so a session
starting one is not building a heuristic the check made redundant.
