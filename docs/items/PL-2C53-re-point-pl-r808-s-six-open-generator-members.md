---
id: PL-2C53
title: Re-point PL-R808's six open generator members at tools/left_behind_check.py, closing each whose question the exact left-behind check now answers
priority: P2
effort: M
status: ready
classes: housekeeping
feature: parallel-sessions
touches: docs/items
added: 2026-09-23
payoff: no session spends an item building another vcs.py heuristic for a member the exact check already answers: each of the six either closes on it or says what it still owns
verify: test "$(grep -l 'left_behind_check.py' docs/items/PL-X5PK-*.md docs/items/PL-CZR6-*.md docs/items/PL-NPWP-*.md docs/items/PL-BYMX-*.md docs/items/PL-B78T-*.md docs/items/PL-1X2C-*.md | wc -l)" -eq 6
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
answers only for a branch whose newest pull request merged. A branch with no
pull request, and every decline, stays with `vcs.orphaned` (`PL-BHVM`). So a
member whose defect is in what `docket stranded`, `flight` or `show` prints is
not answered just because the digest now prints a line. That member keeps its
place, and its brief says what the exact check now covers and what is still
left to it.

**Generator check.** Bookkeeping. The head's own members were left to re-point,
and this item was filed in the commit that closed `PL-R808` (`#932`). That is
the shape `PL-04KR` records for every attributed child to date. The store holds
no other re-point item, so there is no cluster to name.
