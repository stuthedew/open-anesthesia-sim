---
id: PL-P5S0
title: Closing an item needs a pull request number that does not exist until the pull request does, so the closure is always a second commit a fast merge can strand
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: public-history
touches: subprojects/docket/src/docket/checks.py, .claude/skills/docket/SKILL.md, subprojects/docket/tests/test_checks.py
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

**Decision needed.** Which of the three routes closes the window: fill the
number from the merge in a later pass, accept a `done` item with no `pr` until
its closure reaches `main`, or keep the order and make the recovery a command?
The recommendation below is the second, and the answer decides whether the fix
lands in `checks.py`, in `.claude/skills/docket/SKILL.md`, or in both.

**Triaged 2026-09-01 to `needs-decision`,** because the item names three routes
and the choice between them is the work. Grouped with `public-history`, which
holds both halves of why the rule exists: `PL-S4M2` switched `main` to
squash-merge, and `PL-ZQ9C` then required the `pr` field precisely because a
squash discards the branch commit that would otherwise carry the provenance.

**The recommendation, for whoever settles it: option two.** Accept a `done`
item with no `pr` while its closure has not reached `main`, and error only once
it has. That is the only one of the three that closes the window rather than
moving it: the closure commits *with* the work, in one commit, before any pull
request exists, so a fast merge has nothing left to strand. Option one still
needs a later pass somebody has to remember to run, and option three does not
prevent the stranding at all - it only shortens the rescue.

It is not free: an item can still reach `main` with an empty `pr`, and filling
it in afterwards is a follow-up commit. That is strictly better than today,
where the whole closure is stranded and the queue misreports an open gate, but
it should be weighed rather than assumed.
