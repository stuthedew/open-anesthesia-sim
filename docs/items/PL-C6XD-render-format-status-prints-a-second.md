---
id: PL-C6XD
title: render.format_status prints a second independent copy of the RESERVED refusal that no item covers, and no surface anywhere prints the reserved set a session would need to act on either one
status: untriaged
added: 2026-09-16
---

**Problem.** render.format_status prints a second independent copy of the RESERVED refusal that no item covers, and no surface anywhere prints the reserved set a session would need to act on either one

**Found 2026-09-16** while triaging `PL-SYG4`, which is filed against the digest
alone and would leave this one saying the old thing.

**Two copies, one verdict.** `render._release_advice` turns a `RESERVED` offer
into "No release to offer: the roadmap gives 0.5.0 to ... which is unfinished -
the beat below is what is due." `render.format_status` has its own branch on the
same verdict and prints a different sentence - "Not 0.5.0: the roadmap gives that
version to ... `docket wave` for what is due." Both read `offer.kind` and neither
reads the other. `PL-SYG4`'s `touches` names `_release_advice`; answering it
without this leaves `bin/docket status` carrying whichever wording the digest
just stopped using.

**And no surface prints the reserved set at all.** `reserved` does not occur in
`render.py`, and `bin/docket wave` prints Version, Step, Next, Gate, Scope and
Beat only. `#606` gave `Wave` the full list of versions the roadmap has spent -
today `0.4.26`, `0.5.0`, `0.6.0`, `0.7.0` - and a session can see exactly one of
them, the one that happens to collide with this bump, and only in prose. The
guard's answer is legible; its evidence is not.

**Why it matters.** This is the drift `.claude/rules/apparatus-standard.md` calls
duplicated logic, and it is the shape `PL-VFD8` has just been through one layer
down: one fact, two readers, and a fix applied to whichever one the item
happened to name. `PL-SYG4` is about the wording of a refusal, so shipping it
against one of two copies guarantees they disagree - and the cut path has no
guard of its own, so both copies are load-bearing.

**Done when.** The `RESERVED` verdict is rendered from one place, so
`bin/docket digest` and `bin/docket status` cannot disagree about it; a test in
`subprojects/docket/tests/test_release.py` asserts both surfaces on one
arrangement. Whether the reserved set is printed somewhere a session can read -
a `Reserved` line under `bin/docket wave` is the cheap form - is worth deciding
in the same pass and is the smaller half.

**Sequence it with `PL-SYG4`**: this is the refactor that makes that item's
answer land in one place rather than two, and doing it first makes that item
smaller.
