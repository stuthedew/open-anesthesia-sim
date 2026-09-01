---
id: PL-P5S0
title: Closing an item needs a pull request number that does not exist until the pull request does, so the closure is always a second commit a fast merge can strand
status: untriaged
added: 2026-09-01
---

**Problem.** `docket check` errors on an item `marked done but records no
pr`, and the `docket` skill says the number "is known before the merge, so it
goes in the same commit as the closure rather than in a later amend". Both are
right, and together they force an order that cannot be collapsed:

1. commit the work (the item still `ready`, or `make check` fails);
2. push, and open the pull request, which is what mints the number;
3. commit the closure carrying that number, and push again.

Step 3 is a separate push, arriving seconds to minutes after the pull request
opens. On `PL-D2GW` (the digest's release offer contradicting its own plan
line) the owner merged pull request 134 in the 100 seconds that gap lasted.
The merge took the work and left the closure on the branch, so `main` had the
fix while the queue still called the item `ready` and the v0.2.8 gate still
counted it open. Recovering it meant restarting the branch from `main` per
`PL-1Q3S`, cherry-picking one commit, and opening a second pull request for a
one-file change.

**Why it matters.** The window is small but it is open on every item, and what
falls through it is the record rather than the code - the state most likely to
go unnoticed, because everything a reader looks at (the diff, `main`, CI) is
correct. An item that stays `ready` after its work has shipped is offered
again by `docket next`, counted open by `wave`, and holds a gate that has in
fact cleared.

**Where.** The rule is in `.claude/skills/docket/SKILL.md` ("Mode: close out
an item"); the error is `checks.py`'s done-without-`pr`. Options worth
weighing rather than one obvious fix: let the closure record the branch and
have a later pass fill the number from the merge; accept a closure with no
`pr` while the branch is unmerged and error only on `main`; or keep the order
and make the recovery a command instead of a procedure, since the cherry-pick
is mechanical.

**Done when.** Work that has merged cannot leave its item open because the
number arrived a minute late, whichever of those routes is taken.
