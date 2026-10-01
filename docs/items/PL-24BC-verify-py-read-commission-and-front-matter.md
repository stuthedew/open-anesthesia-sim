---
id: PL-24BC
title: verify.py read_commission and front_matter_check find an item's file on the base by startswith(id-) rather than ITEM_FILE_RE and _items_at, a second spelling of the item-file grammar
status: untriaged
feature: recorded-not-inferred
added: 2026-10-01
---

**Problem.** verify.py read_commission and front_matter_check find an item's file on the base by startswith(id-) rather than ITEM_FILE_RE and _items_at, a second spelling of the item-file grammar

**Recorded alternative, from the 2026-10-01 survey.** Use `ITEM_FILE_RE` and `_items_at`. Low confidence: the survey read the call sites, not every path through them. Shape B.
