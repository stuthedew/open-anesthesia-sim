---
id: PL-24BC
title: verify.py read_commission and front_matter_check find an item's file on the base by startswith(id-) rather than ITEM_FILE_RE and _items_at, a second spelling of the item-file grammar
priority: P3
effort: S
status: ready
classes: defect
feature: recorded-not-inferred
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: the next change to the item-file grammar reaches the audit's two readers of it without a second edit
verify: ! grep -qF 'held_name.startswith(f"{item.identifier}-")' subprojects/docket/src/docket/verify.py
---

**Problem.** verify.py read_commission and front_matter_check find an item's file on the base by startswith(id-) rather than ITEM_FILE_RE and _items_at, a second spelling of the item-file grammar

**Recorded alternative, from the 2026-10-01 survey.** Use `ITEM_FILE_RE` and `_items_at`. Low confidence: the survey read the call sites, not every path through them. Shape B.

**Why it matters.** `read_commission` and `front_matter_check` find the base's copy of an item by `startswith(f"{id}-")` where `vcs.ITEM_FILE_RE` and `_items_at` state the item-file grammar. The two agree on every well-formed name today - triage constructed no disagreeing input - so the cost is the next change to the grammar not reaching these two readers, the shape-B case `.claude/rules/apparatus-standard.md` § "Read the fact from its record; where none exists, write one" names.

**Reproduced 2026-10-01.** `subprojects/docket/src/docket/verify.py:1993` and `:2136` each read `held_name.startswith(f"{item.identifier}-")`; `vcs.py:804` holds `ITEM_FILE_RE`.

**Done when.** Both sites find the file through `ITEM_FILE_RE` or `_items_at`, and the `startswith` spelling is gone.

**Generator check.** An instance of `PL-PVW2`'s fact - which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it - filed after that head drained on 2026-09-26. Six such instances filed 2026-10-01 make `PL-KGYT`, this item's head.
