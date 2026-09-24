---
id: PL-KWCY
title: A claimed queue-only branch whose claimed items all close in the same push could arm auto-merge, since that merge erases no live claim, instead of taking a hand merge
priority: P2
effort: S
status: done
classes: defect
milestone: v0.5.9
touches: CLAUDE.md
added: 2026-09-23
closed: 2026-09-23
pr: 961
payoff: a claimed queue-only branch that has closed every item it claims - a triage pass under its housekeeping item, a stranded recovery, a grooming pass's drops - lands by auto-merge instead of waiting for the owner's hand merge, while a branch still holding a claim on an open item stays unarmed
verify: grep -qF "closed in the branch's own copy" CLAUDE.md && grep -qF 'last item it claims arms it' CLAUDE.md
---

**Problem.** A claimed queue-only branch whose claimed items all close in the same push could arm auto-merge, since that merge erases no live claim, instead of taking a hand merge

**Found closing `PL-1MCK`, 2026-09-23.** `PL-1MCK` leaves a captures-only
pull request unarmed whenever the branch holds a claim. That includes the
queue-only claims start mode names: a triage pass under a housekeeping item, a
stranded recovery, a closure of an item `main` holds open. Where such a
branch closes every item it claims in the same push, the merge erases no claim
that work still depends on, yet the pull request now waits for a hand merge.
`PL-QP9Z` already gave the default claim path that cost. The narrower
condition, "unarmed while an item the branch claims is still open in its own
copy", would let those land by themselves. It is a new condition to read at
push time, so it is captured here rather than built under the new-mechanism
pause.

**Why it matters.** Since `PL-1MCK`, every claimed queue-only branch waits for
the project owner's hand merge, even once it has closed everything it claims:
a triage pass under its housekeeping item, a stranded recovery, a grooming pass
whose drops are its claims. The merge would erase only claims on closed items,
which `bin/docket next` never offers, so the wait spends the owner's attention
and protects nothing, and every capture riding the branch waits with it.
`PL-WNCT` exists so that queue-only work reaches `main` without the owner.

**Generator check.** Not a generator, and not a missed re-entry: a narrowing
`PL-1MCK`'s close-out saw and deferred under the new-mechanism pause. It shares
one cause with `PL-QP9Z` and `PL-1MCK`. The unarmed exception named kinds of
claim rather than the state it protects, a claim on an open item, so `PL-QP9Z`
named too few and `PL-1MCK`'s widening took in closed ones. As a head it would
name two items, under the three the generator rule counts. Stating the state
itself ends the series: every claim start mode reads is covered, and a closed
item's claim drops out by construction.

**Done when.** `CLAUDE.md`'s commit-and-push bullet holds a claim's unarmed
state only until its item is closed in the branch's own copy, and says that the
push closing the last item a branch claims arms it while only item files ride
the branch.
