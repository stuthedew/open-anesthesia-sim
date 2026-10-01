---
id: PL-2BWP
title: verify.py item_commits selects an item's commits with git log --grep=<id> over the whole message while other_items_named reads vcs.leading_ids, so a commit citing the id mid-sentence counts as the item's and the two readers can disagree
priority: P2
effort: S
status: ready
classes: defect
feature: recorded-not-inferred
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: an item's audit reads the commits that lead with its id and no commit that merely cites it, the same answer the claim record gives
verify: grep -q 'def test_item_commits_reads_leading_ids_only' subprojects/docket/tests/test_verify.py
---

**Problem.** verify.py item_commits selects an item's commits with git log --grep=\<id> over the whole message while other_items_named reads vcs.leading_ids, so a commit citing the id mid-sentence counts as the item's and the two readers can disagree

**Recorded alternative, from the 2026-10-01 survey.** Select the commits by the `Claim:` trailer or `vcs.leading_ids`, the grammar the claim record and `other_items_named` already use. `PL-087W` covers the selection of removed assertions, not this split. Shape B: two readers of one fact.

**Why it matters.** `item_commits` is what `docket verify` reads an item's work from, and `other_items_named` reads `vcs.leading_ids`. A commit citing an id in its body is the item's to the first reader and not to the second, so one branch's audit can attribute a commit to two items or to the wrong one - the disagreement shape `PL-PVW2` closed on.

**Reproduced 2026-10-01.** On this branch `git log --grep=PL-PVW2 --format=%h origin/main..HEAD` prints `2d7c087a`, `PL-HC8P`'s capture commit, which leads with `PL-HC8P` and cites `PL-PVW2` in its body; `item_commits(root, base, "PL-PVW2")` counts it. `subprojects/docket/src/docket/verify.py:1538` is the `--grep` read.

**Done when.** `item_commits` selects by `vcs.leading_ids`, the subject grammar the claim record and `other_items_named` already read, and a test pins that a commit citing the id mid-body is not the item's.

**Generator check.** An instance of `PL-PVW2`'s fact - which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it - filed after that head drained on 2026-09-26. Six such instances filed 2026-10-01 make `PL-KGYT`, this item's head.
