---
id: PL-KWCY
title: A claimed queue-only branch whose claimed items all close in the same push could arm auto-merge, since that merge erases no live claim, instead of taking a hand merge
status: untriaged
added: 2026-09-23
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
