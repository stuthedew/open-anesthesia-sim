---
id: PL-3BYK
title: docket digest --profile's ref set block counts item-file edits per ref and sums across refs, while the walk holds one entry per identifier, so anyone predicting a diff count from it over-predicts by about 2x on a clone with overlapping long-lived branches
priority: P3
effort: S
status: done
classes: defect
feature: rendered-claim-accuracy
milestone: v0.5.12
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-09-17
closed: 2026-09-26
pr: 1036
verify: grep -q 'def test_the_ref_set_block_names_distinct_item_files' subprojects/docket/tests/test_cli.py
---

**Problem.** docket digest --profile's ref set block counts item-file edits per ref and sums across refs, while the walk holds one entry per identifier, so anyone predicting a diff count from it over-predicts by about 2x on a clone with overlapping long-lived branches

**Found by comparing a prediction against the machine it was made for
(`PL-DMDF`), 2026-09-17.** The `ref set` block exists so a call count is read
next to the input that produced it, which is the whole remedy `PL-XD3C` built
after three scaling models were refuted for being ratios between uncontrolled
inputs. It works for `refs` and `commits`. The `item-file edits` figure is the
one that does not mean what a reader will take it to mean.

**The two quantities, and why they diverge.** `_ref_walk` in
`subprojects/docket/src/docket/vcs.py` counts, per unmerged ref, the distinct
paths `git diff --name-only <fork> <ref> -- docs/items/` names, and sums that
across refs. `branches_in_flight`'s `walk.edited` is a `dict` keyed by item
**identifier** for the whole walk, so an item file edited on ten refs
contributes ten to the profile and one to the walk - and the walk's entry is
then filtered again by `walk.unbounded` and by what is already `in_flight`.

On a fresh container the two nearly coincide, because few refs overlap. On the
project owner's clone they are 2.6x apart, because the ref set is dominated by
long-lived branches all editing the same store: `simulation-lag-input-issue`
(416 item files), `0-3-0-release-workflow` (247), `triage-untriaged-items`
(150), two `codex/*` batches (74 and 75). Measured there: 1,284 summed
per-ref edits, against ~493 identifiers that actually reached `_superseded`.

**Why it matters, and what it cost concretely.** `PL-DMDF` established `diff` at ~0.95 calls per
item-file edit. Applied to that clone's 1,284 the law predicts ~1,353 `diff`
calls; the machine made 654. The law was not wrong - it was measured against a
scratch clone whose synthetic refs touched disjoint files, where the two counts
are the same number. Nothing failed, because the before/after numbers that
mattered were measured rather than derived. But the next reader to divide by
that figure gets an answer that is wrong by a factor that grows with how much
the branches overlap, and the block is printed precisely to be trusted.

**Two routes.** Print the *distinct* item files across the whole walk beside
the per-ref sum - two numbers, and the gap between them is itself the
overlap signal a reader wants. Or rename the field to say it is a per-ref sum.
The first is more useful and is a few lines in `_ref_walk`; the second is
cheaper and pins nothing. Not a fix-now either way: it needs a test over a ref
set with deliberate overlap, which no existing fixture has.

**Done when** the `ref set` block states a figure a reader can divide a
per-item-edit rate by without over-predicting, or names the one it prints as a
per-ref sum, and a test drives two refs editing one item file.

**Worked.** Took the first of the brief's two routes, the one its `verify:`
names: `RefWalk` gains `item_files`, the distinct item files the unmerged refs
edit between them, and the block prints it beside the sum, which it now calls
"item-file edits summed per ref". Distinct is counted by path, the unit the
per-ref figure already counts, not by item id, so a ref that retitles an item
(listed under both names by `--no-renames`) counts two there as it does in its
own row. The brief's `_ref_walk` is `vcs.ref_walk` now, and the walk it
compared against, `branches_in_flight`'s one entry per identifier, is
`claims.holdings`, which asks `vcs._superseded` once per branch; so the
0.95-diff-calls-per-edit rate is not re-derived here, and the change makes the
block say which figure is which. `subprojects/docket/tests/test_vcs_silence.py`
compares `ref_walk`'s counts under git silences and does not name the new
field, which comes from the same per-ref reads as `item_edits`; that file is
outside `touches` and is left as it is. The test builds two branches editing
one item file from `main` and runs `digest --profile` end to end; it fails when
the distinct count is computed as the sum.
