---
id: PL-C8MV
title: PL-SZ56's product-vs-apparatus readout counts tests of apparatus under tests/ as product churn
priority: P2
effort: S
status: ready
classes: docs
feature: planning-cadence
touches: docs/items/, docs/releases/
added: 2026-09-02
verify: python3 tools/doc_check.py check && grep -q 'counts as apparatus' docs/items/PL-SZ56-assess-the-v0-3-0-loop-trial-against-its-pre.md
---

**Problem.** `PL-SZ56`'s readout 1 partitions churn by path: `src/` plus
`tests/` is product, `.claude/`, `tools/`, `subprojects/`, `bin/` and
`Makefile` are apparatus. Some tests under `tests/` test the apparatus rather
than the simulator, and the partition credits them to product.
`tests/unit/test_contrast_check.py` (+284 lines in the v0.3.0 window) tests
`tools/contrast_check.py`; `tests/unit/test_doc_check.py` tests
`tools/doc_check.py`. Both sit on the product side of a readout whose whole
purpose is to detect apparatus becoming the work.

**Why it matters.** The readout is the one asking whether the workflow
machinery has stopped eating the project, so a partition that files
apparatus tests as product biases it in exactly the direction it is meant to
catch. Measured 2026-09-02 over `v0.2.8..11d6be7`, the effect is not
currently decisive — 3,832 vs 1,690 lines as written, 3,548 vs 1,974 with
`test_contrast_check.py` reassigned, so product leads either way — but the
margin is 2.27x against 1.80x, and a smaller product window would flip on it.

**Where.** The readout definition in
`docs/items/PL-SZ56-assess-the-v0-3-0-loop-trial-against-its-pre.md`, and
whatever computes it if Gate 1 turns these readouts into a command.

**Note on timing.** Do not amend `PL-SZ56`'s readout 1 in place without the
treatment its own protocol requires: the v0.3.0 numbers are already known, so
a partition change made now is a post-outcome change and has to be recorded
with its date, its reason, and both scorings, exactly as readout 3's
amendment of 2026-09-02 was. Stating the adjustment in the close-out
alongside the as-written number is the cheaper and more honest option, and is
the recommendation.


**On the `verify:` command.** It greps `PL-SZ56` rather than
`docs/releases/v0.3.0.md`, because that close-out does not exist yet and this brief's first
disposition names the item outright. If the sentence lands in the
close-out instead, move the command with it.

**Done when.** Either `PL-SZ56` records which tests count as apparatus and
why, with both scorings given, or the close-out states the adjustment beside
the as-written figure and this is dropped with that decision recorded.
