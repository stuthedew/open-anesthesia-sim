---
id: PL-5FMC
title: Check each section of docs/INTERFACE.md and the other interface documents against the code, fix each plain fact error, and file each product decision the check finds
priority: P2
effort: M
status: ready
classes: docs
touches: docs/INTERFACE.md, docs/interface-provenance.md, docs/ARCHITECTURE.md, docs/items
added: 2026-11-21
payoff: each sentence of the interface specification that says what the interface shows or does is true of the code, or is an item
verify: grep -qE '^[*][*]Checked 2026-11-2[0-9][.:]' docs/items/PL-5FMC-*.md
sweep: claims in docs/INTERFACE.md and the other interface documents that the code does not do
---

**Problem.** Check each section of docs/INTERFACE.md and the other interface documents against the code, fix each plain fact error, and file each product decision the check finds

**Why it matters.** A blind review of closed work found 133 defects, and 42 of
them were a specification that claims something the code does not do, the
largest category (the one-shot study, `PL-WKKH`). `docs/INTERFACE.md` is the
authoritative statement of what the interface must show and do. A contributor
who trusts a wrong sentence there builds on behaviour that does not exist, and
a reader who trusts it can misread a displayed value.

**What to do.** The project owner asked for this sweep on 2026-11-21
("Do all 3 actually", to the coordinator's offer of an interface-spec check).

1. Read `docs/INTERFACE.md` section by section, and the interface claims of
   `docs/interface-provenance.md` and `docs/ARCHITECTURE.md`. Check each
   statement of what the interface shows or does against `src/` and the tests.
2. Confirm each reported mismatch against the source before acting on it.
3. Where the document is plainly wrong and the code is right, correct the
   sentence. Where the code is plainly wrong against the document, the fix is
   an item of its own, because a code defect needs its regression test.
4. Where the mismatch is a product decision, file an item at
   `needs-decision` with the question for the owner recorded in it.
5. Record the verdict for each section below, dated.

**What it must not do.** Restructure the document: sorting it by reader is
`PL-SY7G`, which waits on `PL-48MX`. Edit a claim that `PL-7CY5`'s build
(one exact step per whole second) will change: note those claims here
instead, because that build is changing `core/` while this sweep runs.

**Done when.** Every section of `docs/INTERFACE.md` has a dated verdict in
this item, each plain fact error is corrected, and each product decision is
an item of its own.
