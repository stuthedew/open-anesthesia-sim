---
id: PL-6T44
title: docket next and wave read status: blocked literally, so an item whose blockers have all closed ranks as unstartable while docket check already prints it as promotable
status: untriaged
feature: docket-store
added: 2026-09-17
---

**Problem.** docket next and wave read status: blocked literally, so an item whose blockers have all closed ranks as unstartable while docket check already prints it as promotable

**Why it matters.** It makes the current milestone read as more stuck than it
is, at exactly the moment a session is deciding what to work on. Measured
2026-09-17: `bin/docket wave` reports v0.5.0 — the case you can branch as "19
closed, 7 open" and five of those seven carry `status: blocked`, so `bin/docket
next` offers only `PL-MN4J` and `PL-49R8` from the whole of the milestone's
Required scope. But `PL-LPLD`'s sole blocker `PL-25KS` and `PL-W7H9`'s sole
blocker `PL-8PSW` both closed in v0.4.26, and `bin/docket check` says so
outright — "PL-LPLD: every blocker has closed; it is ready to promote", the
same for `PL-W7H9` and five others. `PL-LPLD` is the head of the chain the
bookmark half of the milestone sits behind (`PL-LPLD` → `PL-CTD7` → `PL-B8MK`
→ `PL-Z3W6`), so the one item that unblocks three more of the milestone's own
scope was invisible to the command that ranks work.

**The two halves are already computed; nothing joins them.** `check` derives
"every blocker has closed" from the same store `next` and `wave` read, so this
is not new analysis — it is one reading not reaching the other two. A session
that runs `next` without also running `check` never learns the item is
startable, and `next` is the command the workflow prescribes for picking.

**Options, for triage to weigh.**

1. `next` and `wave` treat a `blocked` item whose `blocked-by` ids have all
   closed as startable, and say so in the reason line ("was blocked; every
   blocker closed"). Ranks it where it belongs without editing the store.
2. They leave the ranking alone but name the promotable ids in the same output
   `check` does, so the reader sees them at the moment of choosing.
3. Promotion stays a grooming action and the advisory is made an error, which
   forces the flip before the next `make check` passes.

Option 1 changes no item file and needs no pass to be run; option 3 puts a
queue edit in front of unrelated work. Weigh 1 against 2 on whether a
recomputed status should override what an item declares.

**Found by.** A "what should we do next" session on 2026-09-17, which reached
the answer only by reading `blocked-by` on all five and resolving each root by
hand.
