---
id: PL-1MCK
title: Auto-merge still arms on a claimed branch whose claim is a queue-only commit or rode an earlier push, because PL-QP9Z's exception names only a start claim riding the first push
priority: P2
effort: S
status: done
classes: defect
milestone: v0.5.9
touches: CLAUDE.md
added: 2026-09-23
closed: 2026-09-23
pr: 955
payoff: a session keeps its claim on a pushed branch whatever kind of claim it pushed and whichever push carried it, instead of a needs-decision design round, or a claim pushed before the branch's first item files, arming auto-merge and erasing the claim
verify: grep -q "whichever push carried it" CLAUDE.md
---

**Problem.** Auto-merge still arms on a claimed branch whose claim is a queue-only commit or rode an earlier push, because PL-QP9Z's exception names only a start claim riding the first push

**What the clause keys on, and what it misses.** `CLAUDE.md`'s commit-and-push
bullet arms auto-merge on a branch carrying only item files (`PL-WNCT`), except
that "a start claim riding that push leaves it unarmed" (`PL-QP9Z`).
The reason it gives, "the merge would erase the claim with the branch", is a
property of the branch at the moment of arming. The operative clause reads one
push and one kind of claim. "Start claim" appears in no other document, so a
session maps it to start mode's empty `start` commit. Start mode prescribes two
claims that reach an armable push without that commit riding it:

1. **A queue-only commit that is the claim.**
   `.claude/skills/docket/modes/start.md` § "Mode: start an item" makes a
   `needs-decision` item's design round its claim, read off the item's status
   (`PL-VYSP`). It is item files only, so `PL-WNCT` arms it, and it is not the
   empty `start` commit, so the letter of `PL-QP9Z` does not stop it. Here the
   merge is not the end of the work: the design round goes up before the owner
   answers, and the implementation follows the answer. Once it lands, `main`
   holds a `needs-decision` item that no branch claims, which `bin/docket next`
   ranks like any other (one headed the queue on 2026-09-23, `PL-CWD4`). The
   session then implements the answer on a deleted branch, the restart
   `PL-KNWP` paid for.
2. **A claim that rode an earlier push.** Start mode pushes the empty claim on
   its own, before any work, and then asks for the item's `status`, `feature`
   and `touches` as work begins. A session that pushes that fill, or a design
   round, before its first code holds a branch whose commits touch only
   `docs/items/`. That is the shape `PL-WNCT` opens and arms, at a push the
   claim did not ride. Whether `PL-WNCT` fires there depends on whether "its
   first push" means the branch's first push or its first push carrying files,
   and the text does not settle that.

Neither case has been observed. Both follow from the text, found on 2026-09-23
while auditing `PL-QP9Z` after it merged. A session that reads the rationale
gets both right. One that acts on the operative clause arms auto-merge, and the
guards then read the item as free while it is taken. That is the silent wrong
answer `PL-QP9Z` exists to remove.

**Decision needed.** Should the unarmed condition key on the branch holding a
claim, whichever push carried it and whichever kind it is? `PL-QP9Z` is
ratified (project owner, 2026-09-23), so ordinary evidence reopens its scope.
A case its wording did not cover is that evidence.

**Recommended: yes.** Replace "A start claim riding that push leaves it
unarmed" with a clause that leaves unarmed a branch holding a claim: the empty
start commit, or a queue-only commit start mode reads as one, whether it rode
this push or an earlier one. The change is one clause in the same bullet. It
repairs a rule that exists rather than adding a mechanism, and it costs about
100 resident characters. The alternatives cost more:

- Opening an unarmed pull request at every claim push runs CI for every item
  started, and it contradicts start mode's "a push to a branch with no pull
  request open runs no CI".
- Never arming a captures-only branch reverses `PL-WNCT`.

**Done when.** `CLAUDE.md` states the unarmed condition as the branch holding a
claim, naming the queue-only claim and a claim pushed before the branch's first
item files. Alternatively, the owner declines, and this brief records the
operative clause's letter as the accepted reading.

**Decided 2026-09-23: yes** (project owner, 2026-09-23, ratified, over reading
only a start claim riding the first push). `CLAUDE.md`'s commit-and-push bullet
now says a claim on the branch leaves the pull request unarmed, whichever push
carried it: the empty start commit, or a queue-only commit start mode reads as
one, such as a `needs-decision` design round. A push bringing a claim or
anything but item files disarms it first. That replaces `PL-QP9Z`'s "a start
claim riding that push" and its "a start claim included".

**What it leaves.** Queue-only work a session claims, such as a triage pass
under a housekeeping item or a stranded recovery, now waits for a hand merge
even when it closes its item in the same push. `PL-QP9Z` already gave the
default claim path that cost, and this extends it to the exception claims.
`PL-KWCY` records the narrower condition that would let such a branch arm once
its claimed items are closed.

**Resident cost: 173 characters net**, whitespace-normalised, where the
recommendation estimated about 100. The decision record and the named example
make the difference. Nothing else can move: the arming rule is stated only in
this bullet, and the exception has to be read at the same push. Built under the
new-mechanism pause as a defect in a rule that exists, and at the owner's
request, which lifts the pause for it (`PL-6Q9L`).

`PL-QP9Z`'s own `verify:` greps for the clause this replaces, so it no longer
passes on the new tree. A closed item's fields are its record of what was true
when it closed, so it is left as it stands.
