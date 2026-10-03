---
id: PL-X766
title: tools/doc_check.py _live_item_briefs reads an item's status with its own ITEM_STATUS_RE instead of docket.model's parser, which it already reaches through _read_store
priority: P3
effort: S
status: done
classes: defect
feature: recorded-not-inferred
milestone: v0.5.21
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-01
pr: 1271
payoff: the doc checks read an item's status the way docket does, so a quoted or wrapped value cannot put a closed brief under the live checks
verify: ! grep -qF 'ITEM_STATUS_RE' tools/doc_check.py
---

**Problem.** tools/doc_check.py _live_item_briefs reads an item's status with its own ITEM_STATUS_RE instead of docket.model's parser, which it already reaches through _read_store

**Recorded alternative, from the 2026-10-01 survey.** Use `docket.model`'s item parser, which `doc_check` already reaches through `_read_store`. Shape B.

**Why it matters.** `_live_item_briefs` decides which briefs the doc checks read as live; a status it misreads puts a closed item's brief under the live checks or a live one past them. `docket.model`'s parser, which `_read_store` already builds, reads a quoted or wrapped value whole since `PL-9HD1`; the regex reads the first token after `status:`.

**Reproduced 2026-10-01.** `ITEM_STATUS_RE` (`tools/doc_check.py:3869`) on `status: "done"` returns `"done"` with its quotes, a value in no status set, where `docket.model.parse_item` reads `done`. No shipped item quotes its status today, so the disagreement is by construction - the state `PL-PVW2` recorded its members in.

**Done when.** `_live_item_briefs` reads status from the store `_read_store` builds, `ITEM_STATUS_RE` is gone, and the live-brief checks answer as before on the current store.

**Generator check.** An instance of `PL-PVW2`'s fact - which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it - filed after that head drained on 2026-09-26. Six such instances filed 2026-10-01 make `PL-KGYT`, this item's head.
