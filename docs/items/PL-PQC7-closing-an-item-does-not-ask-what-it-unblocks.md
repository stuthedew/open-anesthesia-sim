---
id: PL-PQC7
title: Closing an item does not ask what it unblocks, so every promotable item waits for someone to run a deliberate grooming pass
status: untriaged
added: 2026-09-20
---

**Problem.** Closing an item does not ask what it unblocks, so every promotable item waits for someone to run a deliberate grooming pass

**Found by `PL-8G48`, 2026-09-20**, which was the second grooming pass in four
days over the same advisory, and which merged with `PL-CHQY` - a second session's
item for the identical batch, filed the same day.

**The mechanism.** `bin/docket check` prints "every blocker has closed; it is
ready to promote" whenever a blocker closes. Nothing routes that line to
anybody: it is a standing advisory that only a session running a deliberate
grooming pass ever acts on, and such a pass has to be noticed, filed and
triaged before it can be run. In the meantime `bin/docket next` reads `status`
literally, so the items sit unofferable.

**The recommendation this records** was made in `PL-CHQY`'s own brief and put to
the project owner in the reply that filed it; `PL-CHQY` has since closed, so
without this item the recommendation exists nowhere in the tree. It is: make
*"what does this close unblock?"* part of the `docket` skill's close-out, where
the session closing an item is the one that already knows what its closure
means, rather than leaving the question to a later session reading a store it
has no context for.

**Why that placement rather than a check.** The decidable half - which items name
this one in `blocked-by`, and whether all their blockers are now closed - is
already computed and already printed. What is missing is judgment, and this pass
measured how much: of four items the advisory named, one was promotable, one had
already been done inside its own blocker, one had a user-facing question written
into it, and one was held by two conditions nobody had written down. The session
that closes the blocker is the cheapest place to get that judgment, because it
is holding the context the judgment needs.

**Related, and not a duplicate.** `PL-6T44` (docket next and wave read `status:
blocked` literally) is the *ranking* half of the same problem and is a recorded
generator at `needs-decision`; its three options all change what the commands
print. This is the *routing* half: a fourth route that changes when the question
is asked rather than how the answer is displayed. Whoever answers `PL-6T44`
should read this item first - it may be that one fix makes the other
unnecessary, and deciding that is part of `PL-6T44`'s decision rather than this
item's.
