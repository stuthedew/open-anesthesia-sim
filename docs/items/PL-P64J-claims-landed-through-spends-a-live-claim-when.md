---
id: PL-P64J
title: claims._landed_through spends a live claim when the branch, as of some commit after the claim, only restores files to content the default branch held before the fork, because it splits that commit against the base's ever-held blob set: a claimed branch retiring a feature by restoring files reads as merged, and its item as unheld
status: untriaged
feature: pre-fork-content
added: 2026-09-26
---

**Problem.** claims._landed_through spends a live claim when the branch, as of some commit after the claim, only restores files to content the default branch held before the fork, because it splits that commit against the base's ever-held blob set: a claimed branch retiring a feature by restoring files reads as merged, and its item as unheld

**Reasoned from the code on 2026-09-26, not yet run.** Found while fixing
`PL-RLTK`. A branch holding a claim and one commit that restores a file to a
blob `main` held before the fork: that commit's `added` blobs are all in
`refs.base_blobs`, so it passes the prefilter, and `_landing_split` against the
same ever-held set reads it as wholly landed, so the claim is spent. Before
`PL-RLTK`, `_unlanded_refs` excluded such a branch outright, so its claims were
never read; the visible answer, an unheld item, is the same either way.

It was left out of `PL-RLTK`'s fix on purpose. `_landed_through` splits an
older commit against the *tip's* fork, and below a grafted horizon it relies on
base commits reading as landed (`PL-W1LN`, `PL-N162`), so moving it to the
since-the-fork set needs each commit's own fork and a fresh look at that case.
`claims.py` is Stream B's file in `PL-NZC0`'s trial.
