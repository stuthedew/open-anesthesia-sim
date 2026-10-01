---
id: PL-2BWP
title: verify.py item_commits selects an item's commits with git log --grep=<id> over the whole message while other_items_named reads vcs.leading_ids, so a commit citing the id mid-sentence counts as the item's and the two readers can disagree
status: untriaged
feature: recorded-not-inferred
added: 2026-10-01
---

**Problem.** verify.py item_commits selects an item's commits with git log --grep=\<id> over the whole message while other_items_named reads vcs.leading_ids, so a commit citing the id mid-sentence counts as the item's and the two readers can disagree

**Recorded alternative, from the 2026-10-01 survey.** Select the commits by the `Claim:` trailer or `vcs.leading_ids`, the grammar the claim record and `other_items_named` already use. `PL-087W` covers the selection of removed assertions, not this split. Shape B: two readers of one fact.
