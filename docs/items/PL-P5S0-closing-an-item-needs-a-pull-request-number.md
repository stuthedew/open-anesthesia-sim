---
id: PL-P5S0
title: Closing an item needs a pull request number that does not exist until the pull request does, so the closure is always a second commit a fast merge can strand
priority: P2
effort: S
status: done
classes: defect, infra
feature: public-history
milestone: v0.2.8
touches: subprojects/docket/src/docket/checks.py, .claude/skills/docket/SKILL.md, subprojects/docket/tests/test_checks.py
added: 2026-09-01
closed: 2026-09-01
pr: 140
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'marked done on' subprojects/docket/src/docket/checks.py
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

**Settled 2026-09-01 (project owner): error only on `main`.** `docket check`
accepts a `done` item carrying no `pr` while its closure has not reached the
default base, and raises the error only once it has. The closure then commits
*with* the work, in one commit, before any pull request exists, so the window
this item is about does not open at all. The residual cost is accepted: an item
can still land on `main` with an empty `pr`, and filling it in is a follow-up
commit - strictly better than today, where the whole closure strands and the
queue misreports an open gate.

**The primitive already exists.** `checks.py` imports `PullRequestHistory` from
`vcs` and `LandedReport` from `verify`, so it already reasons about git state,
and `vcs._items_at(ref, ...)` reads the item files as they stand at a ref. The
question the new gate asks is exactly that: does this item read `status: done`
at the default base? Absent from the base entirely means a new item, which is
accepted.

**It must decline rather than guess.** A shallow clone, a bare checkout, or no
git at all cannot answer whether a closure has reached `main`, and a check that
silently passes in that case is worse than none - it would accept every
unfilled `pr` in CI. Report it as not-checked, the way `PL-XCYB` established
for the provenance reader, rather than defaulting either way.

**Verify.** Run before being written down: it exits 1 today, the suite half
green (54 passed) and the `grep` half failing because the message does not
exist yet. The command deliberately avoids `-k` (`PL-5QKT`) and carries no
outer quotes (`PL-MZH2`).

**Built 2026-09-01.** `vcs.ClosureReport` and `vcs.closures_on_base` read
whether each closure in question already stands on the default base;
`checks._check_closures` owes a `pr` only for those, and `cli`'s `check`
command supplies it. The per-item unconditional error is gone.

**It does not decline on a shallow clone,** which is the point that makes it
usable: `merged_pull_requests` declines there because it needs history a
shallow clone answers wrongly, but this needs one tree read, and `git show
<ref>:<path>` is correct however truncated the history behind the ref is. An
agent session normally runs in a shallow clone, so a reader that declined
there would decline in exactly the case the rule exists for. It declines only
when no default branch resolves at all.

**Proven both ways against the real store** before the tests were written: a
new item marked `done` with no `pr` reports 0 errors, and `PL-TH9V` with its
`pr` stripped reports ``marked done on `origin/main` but records no `pr` ``.
Five unit tests cover the four judgments plus the caller that does not ask.

**One existing test asserted the old rule** and was rewritten rather than
weakened: the `closed` date is answerable from the store and stays owed
unconditionally, while the `pr` half moved to the landed case.

**The skill was the other half of the fix.** `.claude/skills/docket/SKILL.md`
told sessions the number "is known before the merge, so it goes in the same
commit as the closure", which is what forced the second push. Close-out now
says to commit the closure *with the work* and fill `pr` in afterwards.

**Verify.** Refined while building: the recorded grep targeted the message
text, which interpolates the base name, so it greps `marked done on` instead -
absent at `HEAD`, present after. It avoids `-k` (`PL-5QKT`) and carries no
outer quotes (`PL-MZH2`).

**Closed under its own new rule,** with `pr` empty in the commit that carries
the work - which is the shape this change exists to make legal.
