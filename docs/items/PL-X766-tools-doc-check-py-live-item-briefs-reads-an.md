---
id: PL-X766
title: tools/doc_check.py _live_item_briefs reads an item's status with its own ITEM_STATUS_RE instead of docket.model's parser, which it already reaches through _read_store
status: untriaged
feature: recorded-not-inferred
added: 2026-10-01
---

**Problem.** tools/doc_check.py _live_item_briefs reads an item's status with its own ITEM_STATUS_RE instead of docket.model's parser, which it already reaches through _read_store

**Recorded alternative, from the 2026-10-01 survey.** Use `docket.model`'s item parser, which `doc_check` already reaches through `_read_store`. Shape B.
