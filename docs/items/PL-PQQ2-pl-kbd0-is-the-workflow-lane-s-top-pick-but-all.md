---
id: PL-PQQ2
title: PL-KBD0 is the workflow lane's top pick but all three live instances its brief names are now closed, and no open item at ready or needs-decision carries a blocked-by field
priority: P2
effort: S
status: ready
classes: defect, docs
feature: planning-cadence
touches: docs/items/PL-KBD0-a-blocked-by-edge-with-no-status-blocked-is.md
added: 2026-09-12
verify: python3 tools/doc_check.py check && grep -qF 'PL-PQQ2' docs/items/PL-KBD0-a-blocked-by-edge-with-no-status-blocked-is.md
---

**Problem.** PL-KBD0 is the workflow lane's top pick but all three live instances its brief names are now closed, and no open item at ready or needs-decision carries a blocked-by field

**Confirmed at triage, 2026-09-12.** All three instances `PL-KBD0` names are
closed - `PL-SN2C`, `PL-LKRP` and `PL-S4M2` are each `status: done`, and so is
`PL-GS5X`, the blocker `PL-LKRP` declared. Across the whole store, sixteen open
items carry a `blocked-by` field and every one of them is already at
`status: blocked`; no item at `ready` or `needs-decision` declares an open
blocker. So the contradiction the check would refuse does not exist in the store
today, and `PL-KBD0`'s brief - including the paragraph headed "State on
2026-09-05, at triage" that already anticipated this - is a week out of date
about which of its instances survive.

**Why it matters.** `PL-KBD0` is the workflow lane's top pick, so it is the item
the digest hands the next workflow session, and that session will open a brief
whose live proof is gone and whose "Decision needed" is argued from two
instances that both closed. The decision itself is still real - nothing stops the
next author declaring `blocked-by` and leaving the status at `ready` - but it has
to be decided on the general case rather than on instances, and the brief does
not currently say that.

This is the `PL-LKGL` staleness problem landing on the single item most likely to
be started next, which is why it is worth its own pass rather than waiting for
`PL-6ZQY`'s sweep.

**Done when.** `PL-KBD0`'s brief states the store's current position - no open
item declares an open blocker, so a check landing today catches nothing - and
argues its decision on the general case, with the closed instances kept as
history rather than presented as live proof.
