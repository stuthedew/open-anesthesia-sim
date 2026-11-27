---
id: PL-VW5V
title: The area layout adapter walks a split's path with its own copy of the layout model's _split_at
priority: P2
effort: S
status: ready
classes: defect
feature: one-source-of-truth
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/layout/model.py, tests/integration/test_layout_adapter.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no learner sees a wrong value from it; the release waits on the owner test drive and two live safety entries, so it is deferred rather than holding the release (triage 2026-11-27)
added: 2026-11-23
filed-pr: 2306
payoff: a change to how a layout path is read is made once, and a path past the last child fails the same way everywhere
---

**Problem.** `_split_at` in `src/anesthesia_sim/app/area_layout.py` walks a path down a layout tree to a split and raises `LookupError` when it finds none. `src/anesthesia_sim/layout/model.py` has its own `_split_at`, built on `_node_at`, which walks the same path and raises `NotInLayout`. The two walks differ: the adapter's stops at the first Area and does not check that each index is in range, so a path that runs past the last child raises `IndexError` there and `NotInLayout` in the model. A change to how a path is read must be made twice, and a test of one copy says nothing about the other.

`PL-PZSF` found it on 2026-11-23, while making `LayoutModel.edges` call the model's `_split_at`.

**What to do.** Give the adapter one way to reach a split through the model, such as a public `LayoutModel.split_at(path)` or a function in `layout/model.py` that both use, and remove the adapter's copy. Keep the adapter's two callers, `_lay_out` and `_drawn_position`, raising what they raise today, or say in the item why that changes.

**Why it matters.** A change to how a layout path is read has to be made twice, and the two copies already disagree on a path that runs past the last child: the adapter raises `IndexError` where the model raises `NotInLayout`. A test of one copy says nothing about the other.

**Reproduced 2026-11-27.** On `main` at `f653c1eb`, `_split_at` is defined in both `src/anesthesia_sim/app/area_layout.py` and `src/anesthesia_sim/layout/model.py`. Both were present at the freeze commit `817a4d88`.

**Done when.** The adapter reaches a split only through `layout/model.py`, its own `_split_at` is gone, and a test shows that `_lay_out` and `_drawn_position` raise what they raised before for a path past the last child, or the item records why that changes.

**Generator check.** A second copy of a fact the layout model owns, so classed `defect` under `CLAUDE.md`'s rule that a shared fact has one source of truth. `PL-PZSF` found it while sorting mutation survivors. No head states how a layout path is walked to a split, and no other open item copies it, so a one-off.
