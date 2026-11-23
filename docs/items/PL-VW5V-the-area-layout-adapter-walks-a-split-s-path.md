---
id: PL-VW5V
title: The area layout adapter walks a split's path with its own copy of the layout model's _split_at
status: untriaged
feature: one-source-of-truth
added: 2026-11-23
filed-pr: 2306
---

**Problem.** `_split_at` in `src/anesthesia_sim/app/area_layout.py` walks a path down a layout tree to a split and raises `LookupError` when it finds none. `src/anesthesia_sim/layout/model.py` has its own `_split_at`, built on `_node_at`, which walks the same path and raises `NotInLayout`. The two walks differ: the adapter's stops at the first Area and does not check that each index is in range, so a path that runs past the last child raises `IndexError` there and `NotInLayout` in the model. A change to how a path is read must be made twice, and a test of one copy says nothing about the other.

`PL-PZSF` found it on 2026-11-23, while making `LayoutModel.edges` call the model's `_split_at`.

**What to do.** Give the adapter one way to reach a split through the model, such as a public `LayoutModel.split_at(path)` or a function in `layout/model.py` that both use, and remove the adapter's copy. Keep the adapter's two callers, `_lay_out` and `_drawn_position`, raising what they raise today, or say in the item why that changes.
