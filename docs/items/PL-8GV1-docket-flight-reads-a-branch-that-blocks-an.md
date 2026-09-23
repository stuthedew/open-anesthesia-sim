---
id: PL-8GV1
title: docket flight reads a branch that blocks an item it never claimed as a note, so docket next goes on offering an item a grooming pass is parking until the pass merges: PL-8FJK's closure promotion reads only the closed statuses
status: untriaged
feature: parallel-sessions
added: 2026-09-22
---

**Problem.** docket flight reads a branch that blocks an item it never claimed as a note, so docket next goes on offering an item a grooming pass is parking until the pass merges: PL-8FJK's closure promotion reads only the closed statuses

**Found 2026-09-22 by `PL-8FJK`'s session and not built there, because the
owner's request named closure.** A grooming pass that sets an item to
`blocked` in a queue-only commit leading with its id reads as a note, so
`docket next` offers the item until the pass merges; a second session starting
it collides with the pass in the item file and works an item the pass has
parked - the cost `PL-8FJK` removed for a drop. `vcs._own_edit_claims` reads
`CLOSED_STATUSES` at the branch's tip; "a status `docket next` does not offer,
where the base's copy is one it does" is the one-predicate widening. Not
observed yet: nobody has counted how often a pass blocks a startable item in a
queue-only commit, which is the number that says whether this is worth
building.
